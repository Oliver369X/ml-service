"""
Pattern Analyzer using Deep Learning (TensorFlow)
Analyzes spending patterns and generates insights
"""
import os
from typing import List, Dict
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import tensorflow as tf
from tensorflow import keras
from sklearn.preprocessing import StandardScaler
import pickle

from ..config import get_settings
from ..utils.logger import logger

settings = get_settings()


class PatternAnalyzer:
    """
    Analizador de patrones de gasto usando Deep Learning
    Usa una red neuronal para detectar patrones complejos
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize pattern analyzer
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or settings.pattern_model_path
        self.scaler_path = self.model_path.replace('.h5', '_scaler.pkl')
        self.model = None
        self.scaler = StandardScaler()
        self.is_trained = False
        
        # Cargar modelo si existe
        if os.path.exists(self.model_path):
            self.load_model()
    
    def extract_features(self, transactions: List[Dict]) -> np.ndarray:
        """
        Extract features from transactions for pattern analysis
        
        Features:
        - Daily total amount
        - Day of week
        - Weekend indicator
        - Category distribution (one-hot encoded top categories)
        - Rolling averages (7, 14, 30 days)
        - Trend indicators
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Feature matrix
        """
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Ensure date is datetime
        df['date'] = pd.to_datetime(df['date'])
        df = df.sort_values('date')
        
        # Aggregate by day
        daily = df.groupby('date').agg({
            'amount': 'sum',
            'id': 'count'  # number of transactions per day
        }).reset_index()
        daily.columns = ['date', 'total_amount', 'num_transactions']
        
        # Date features
        daily['day_of_week'] = daily['date'].dt.dayofweek
        daily['is_weekend'] = (daily['day_of_week'] >= 5).astype(int)
        daily['day_of_month'] = daily['date'].dt.day
        daily['month'] = daily['date'].dt.month
        
        # Rolling features
        daily['rolling_7'] = daily['total_amount'].rolling(window=7, min_periods=1).mean()
        daily['rolling_14'] = daily['total_amount'].rolling(window=14, min_periods=1).mean()
        daily['rolling_30'] = daily['total_amount'].rolling(window=30, min_periods=1).mean()
        
        # Trend
        daily['trend'] = daily['total_amount'].diff().fillna(0)
        
        # Volatility (standard deviation)
        daily['volatility'] = daily['total_amount'].rolling(window=7, min_periods=1).std().fillna(0)
        
        # Category distribution (top categories)
        top_categories = df['category'].value_counts().head(5).index.tolist() if 'category' in df.columns else []
        for cat in top_categories:
            cat_daily = df[df['category'] == cat].groupby('date')['amount'].sum()
            daily[f'cat_{cat}'] = daily['date'].map(cat_daily).fillna(0)
        
        # Select feature columns
        feature_columns = [
            'total_amount', 'num_transactions', 'day_of_week', 'is_weekend',
            'day_of_month', 'month', 'rolling_7', 'rolling_14', 'rolling_30',
            'trend', 'volatility'
        ]
        
        # Add category columns
        feature_columns.extend([col for col in daily.columns if col.startswith('cat_')])
        
        # Get features
        features = daily[feature_columns].fillna(0).values
        
        return features
    
    def build_model(self, input_dim: int) -> keras.Model:
        """
        Build neural network for pattern detection
        
        Args:
            input_dim: Number of input features
            
        Returns:
            Keras model
        """
        model = keras.Sequential([
            keras.layers.Dense(128, activation='relu', input_shape=(input_dim,)),
            keras.layers.Dropout(0.3),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dropout(0.2),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(16, activation='relu'),
            # Output: embedding representation of spending patterns
            keras.layers.Dense(8, activation='sigmoid', name='pattern_embedding')
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, transactions: List[Dict], epochs: int = 50) -> Dict:
        """
        Train the pattern analyzer
        
        Uses unsupervised learning (autoencoder approach)
        
        Args:
            transactions: Historical transactions
            epochs: Number of training epochs
            
        Returns:
            Training metrics
        """
        logger.info(f"Training pattern analyzer with {len(transactions)} transactions...")
        
        # Extract features
        features = self.extract_features(transactions)
        
        # Normalize features
        X = self.scaler.fit_transform(features)
        
        # Build model (autoencoder: X -> embedding -> X)
        input_dim = X.shape[1]
        
        # Encoder
        encoder_input = keras.layers.Input(shape=(input_dim,))
        encoded = keras.layers.Dense(128, activation='relu')(encoder_input)
        encoded = keras.layers.Dropout(0.3)(encoded)
        encoded = keras.layers.Dense(64, activation='relu')(encoded)
        encoded = keras.layers.Dropout(0.2)(encoded)
        encoded = keras.layers.Dense(32, activation='relu')(encoded)
        embedding = keras.layers.Dense(8, activation='relu', name='embedding')(encoded)
        
        # Decoder
        decoded = keras.layers.Dense(32, activation='relu')(embedding)
        decoded = keras.layers.Dense(64, activation='relu')(decoded)
        decoded = keras.layers.Dense(128, activation='relu')(decoded)
        decoder_output = keras.layers.Dense(input_dim, activation='linear')(decoded)
        
        # Autoencoder model
        autoencoder = keras.Model(encoder_input, decoder_output)
        autoencoder.compile(optimizer='adam', loss='mse', metrics=['mae'])
        
        # Train
        history = autoencoder.fit(
            X, X,
            epochs=epochs,
            batch_size=32,
            validation_split=0.2,
            verbose=0,
            callbacks=[
                keras.callbacks.EarlyStopping(patience=10, restore_best_weights=True)
            ]
        )
        
        # Save trained autoencoder
        self.model = autoencoder
        
        # Create encoder model (for pattern extraction)
        self.encoder = keras.Model(encoder_input, embedding)
        
        self.is_trained = True
        
        # Save models
        self.save_model()
        
        final_loss = history.history['loss'][-1]
        final_val_loss = history.history['val_loss'][-1]
        
        logger.info(f"Pattern analyzer trained. Loss: {final_loss:.4f}, Val Loss: {final_val_loss:.4f}")
        
        return {
            'num_samples': len(transactions),
            'loss': float(final_loss),
            'val_loss': float(final_val_loss),
            'epochs_trained': len(history.history['loss'])
        }
    
    def analyze_patterns(self, transactions: List[Dict]) -> Dict:
        """
        Analyze spending patterns
        
        Args:
            transactions: Recent transactions to analyze
            
        Returns:
            Pattern analysis with insights
        """
        if not self.is_trained:
            logger.warning("Pattern analyzer not trained. Using rule-based analysis.")
            return self._analyze_patterns_default(transactions)
        
        # Extract features
        features = self.extract_features(transactions)
        X = self.scaler.transform(features)
        
        # Get pattern embedding
        embeddings = self.encoder.predict(X, verbose=0)
        
        # Analyze embeddings
        avg_embedding = np.mean(embeddings, axis=0)
        std_embedding = np.std(embeddings, axis=0)
        
        # Reconstruct to find anomalies
        reconstructions = self.model.predict(X, verbose=0)
        reconstruction_errors = np.mean((X - reconstructions) ** 2, axis=1)
        
        # Identify pattern types based on embedding
        patterns = self._interpret_embeddings(embeddings, transactions)
        
        # Generate insights
        insights = self._generate_insights(transactions, reconstruction_errors)
        
        return {
            'pattern_type': self._classify_pattern(avg_embedding),
            'patterns': patterns,
            'insights': insights,
            'stability_score': float(1 / (1 + np.mean(std_embedding))),
            'unusual_days': int(np.sum(reconstruction_errors > np.percentile(reconstruction_errors, 90)))
        }
    
    def _classify_pattern(self, embedding: np.ndarray) -> str:
        """
        Classify overall spending pattern
        
        Args:
            embedding: Pattern embedding vector
            
        Returns:
            Pattern type
        """
        # Simple classification based on embedding values
        if np.mean(embedding) > 0.6:
            return "high_spender"
        elif np.mean(embedding) < 0.3:
            return "low_spender"
        elif np.std(embedding) > 0.3:
            return "irregular_spender"
        else:
            return "consistent_spender"
    
    def _interpret_embeddings(self, embeddings: np.ndarray, transactions: List[Dict]) -> List[Dict]:
        """
        Interpret pattern embeddings
        
        Args:
            embeddings: Pattern embeddings
            transactions: Original transactions
            
        Returns:
            List of detected patterns
        """
        patterns = []
        
        df = pd.DataFrame(transactions)
        df['date'] = pd.to_datetime(df['date'])
        
        # Detect weekend vs weekday patterns
        df['is_weekend'] = df['date'].dt.dayofweek >= 5
        weekend_avg = df[df['is_weekend']]['amount'].mean() if 'amount' in df.columns else 0
        weekday_avg = df[~df['is_weekend']]['amount'].mean() if 'amount' in df.columns else 0
        
        if weekend_avg > weekday_avg * 1.5:
            patterns.append({
                'type': 'weekend_spender',
                'description': 'Gastas significativamente más los fines de semana',
                'impact': 'high'
            })
        
        # Detect monthly patterns
        df['day'] = df['date'].dt.day
        start_month = df[df['day'] <= 10]['amount'].mean() if 'amount' in df.columns else 0
        end_month = df[df['day'] >= 20]['amount'].mean() if 'amount' in df.columns else 0
        
        if start_month > end_month * 1.3:
            patterns.append({
                'type': 'early_month_spender',
                'description': 'Gastas más al inicio del mes',
                'impact': 'medium'
            })
        
        return patterns
    
    def _generate_insights(self, transactions: List[Dict], errors: np.ndarray) -> List[Dict]:
        """
        Generate insights from analysis
        
        Args:
            transactions: Transactions
            errors: Reconstruction errors
            
        Returns:
            List of insights
        """
        insights = []
        
        df = pd.DataFrame(transactions)
        
        # Total spending insight
        total = df['amount'].sum() if 'amount' in df.columns else 0
        avg_daily = total / len(df) if len(df) > 0 else 0
        
        insights.append({
            'category': 'spending_summary',
            'message': f'Promedio diario de gastos: ${avg_daily:.2f}',
            'severity': 'INFO'
        })
        
        # Variability insight
        if np.std(errors) > np.mean(errors):
            insights.append({
                'category': 'variability',
                'message': 'Tus gastos son muy variables. Considera crear un presupuesto más estricto.',
                'severity': 'WARNING'
            })
        
        # Top category insight
        if 'category' in df.columns:
            top_category = df.groupby('category')['amount'].sum().idxmax()
            top_amount = df.groupby('category')['amount'].sum().max()
            
            insights.append({
                'category': 'top_spending',
                'message': f'Tu mayor gasto es en {top_category}: ${top_amount:.2f}',
                'severity': 'INFO'
            })
        
        return insights
    
    def _analyze_patterns_default(self, transactions: List[Dict]) -> Dict:
        """
        Default rule-based pattern analysis
        
        Args:
            transactions: Transactions to analyze
            
        Returns:
            Basic pattern analysis
        """
        df = pd.DataFrame(transactions)
        
        return {
            'pattern_type': 'unknown',
            'patterns': [],
            'insights': [
                {
                    'category': 'info',
                    'message': 'Análisis básico. Entrena el modelo para insights avanzados.',
                    'severity': 'INFO'
                }
            ],
            'stability_score': 0.5,
            'unusual_days': 0
        }
    
    def save_model(self):
        """Save model to disk"""
        if not self.model:
            logger.warning("No model to save")
            return
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        # Save TensorFlow model
        self.model.save(self.model_path)
        
        # Save encoder
        encoder_path = self.model_path.replace('.h5', '_encoder.h5')
        self.encoder.save(encoder_path)
        
        # Save scaler
        with open(self.scaler_path, 'wb') as f:
            pickle.dump(self.scaler, f)
        
        logger.info(f"Pattern analyzer saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        try:
            # Load models
            self.model = keras.models.load_model(self.model_path)
            
            encoder_path = self.model_path.replace('.h5', '_encoder.h5')
            if os.path.exists(encoder_path):
                self.encoder = keras.models.load_model(encoder_path)
            
            # Load scaler
            if os.path.exists(self.scaler_path):
                with open(self.scaler_path, 'rb') as f:
                    self.scaler = pickle.load(f)
            
            self.is_trained = True
            
            logger.info(f"Pattern analyzer loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading pattern analyzer: {e}")
            self.is_trained = False

