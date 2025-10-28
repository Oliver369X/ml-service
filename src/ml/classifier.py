"""
Transaction Classifier using Random Forest and TF-IDF
Classifies transaction descriptions into categories
"""
import pickle
import os
from typing import List, Dict, Tuple
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import LabelEncoder
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import re

from ..config import get_settings
from ..utils.logger import logger

settings = get_settings()

# Download NLTK data (solo primera vez)
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)


class TransactionClassifier:
    """
    Clasificador de transacciones usando Random Forest
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize classifier
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or settings.classifier_model_path
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            ngram_range=(1, 2),
            stop_words='english'
        )
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=20,
            random_state=42,
            n_jobs=-1
        )
        self.label_encoder = LabelEncoder()
        self.categories = []
        self.is_trained = False
        
        # Cargar modelo si existe
        if os.path.exists(self.model_path):
            self.load_model()
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess transaction description
        
        Args:
            text: Raw transaction description
            
        Returns:
            Cleaned text
        """
        # Lowercase
        text = text.lower()
        
        # Remove special characters and numbers
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra spaces
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Tokenize
        tokens = word_tokenize(text)
        
        # Remove stopwords
        stop_words = set(stopwords.words('english'))
        tokens = [t for t in tokens if t not in stop_words]
        
        return ' '.join(tokens)
    
    def train(self, texts: List[str], categories: List[str]) -> Dict:
        """
        Train the classifier
        
        Args:
            texts: List of transaction descriptions
            categories: List of corresponding categories
            
        Returns:
            Training metrics
        """
        logger.info(f"Training classifier with {len(texts)} samples...")
        
        # Preprocess texts
        processed_texts = [self.preprocess_text(t) for t in texts]
        
        # Vectorize
        X = self.vectorizer.fit_transform(processed_texts)
        
        # Encode labels
        y = self.label_encoder.fit_transform(categories)
        
        # Train model
        self.model.fit(X, y)
        
        # Store categories
        self.categories = self.label_encoder.classes_.tolist()
        self.is_trained = True
        
        # Calculate training accuracy
        train_accuracy = self.model.score(X, y)
        
        # Save model
        self.save_model()
        
        logger.info(f"Classifier trained successfully. Accuracy: {train_accuracy:.2%}")
        
        return {
            'accuracy': train_accuracy,
            'num_samples': len(texts),
            'num_categories': len(self.categories),
            'categories': self.categories
        }
    
    def predict(self, text: str, top_k: int = 3) -> List[Dict[str, any]]:
        """
        Predict category for a transaction
        
        Args:
            text: Transaction description
            top_k: Number of top predictions to return
            
        Returns:
            List of predictions with category and confidence
        """
        if not self.is_trained:
            logger.warning("Classifier not trained. Using default categories.")
            return self._predict_default(text)
        
        # Preprocess
        processed = self.preprocess_text(text)
        
        # Vectorize
        X = self.vectorizer.transform([processed])
        
        # Get probabilities
        probabilities = self.model.predict_proba(X)[0]
        
        # Get top K predictions
        top_indices = np.argsort(probabilities)[-top_k:][::-1]
        
        predictions = []
        for idx in top_indices:
            category = self.label_encoder.classes_[idx]
            confidence = float(probabilities[idx])
            
            predictions.append({
                'category': category,
                'confidence': confidence
            })
        
        return predictions
    
    def _predict_default(self, text: str) -> List[Dict[str, any]]:
        """
        Default predictions when model is not trained
        
        Args:
            text: Transaction description
            
        Returns:
            Default predictions
        """
        text_lower = text.lower()
        
        # Simple keyword-based classification
        if any(word in text_lower for word in ['uber', 'taxi', 'bus', 'metro', 'transport']):
            return [{'category': 'Transport', 'confidence': 0.7}]
        elif any(word in text_lower for word in ['restaurant', 'food', 'cafe', 'pizza', 'burger']):
            return [{'category': 'Food', 'confidence': 0.7}]
        elif any(word in text_lower for word in ['netflix', 'spotify', 'subscription', 'gym']):
            return [{'category': 'Subscriptions', 'confidence': 0.7}]
        elif any(word in text_lower for word in ['supermarket', 'grocery', 'walmart', 'store']):
            return [{'category': 'Groceries', 'confidence': 0.7}]
        elif any(word in text_lower for word in ['rent', 'electricity', 'water', 'internet']):
            return [{'category': 'Bills', 'confidence': 0.7}]
        else:
            return [{'category': 'Other', 'confidence': 0.5}]
    
    def save_model(self):
        """Save model to disk"""
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'vectorizer': self.vectorizer,
                'label_encoder': self.label_encoder,
                'categories': self.categories,
                'is_trained': self.is_trained
            }, f)
        
        logger.info(f"Model saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            self.model = data['model']
            self.vectorizer = data['vectorizer']
            self.label_encoder = data['label_encoder']
            self.categories = data['categories']
            self.is_trained = data.get('is_trained', True)
            
            logger.info(f"Model loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            self.is_trained = False

