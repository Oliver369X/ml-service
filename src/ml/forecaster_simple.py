"""
Simple Expense Forecasting using Linear Trend (Fallback)
"""
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import joblib
import warnings
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error

from ..utils.logger import logger

warnings.filterwarnings('ignore')


class SimpleExpenseForecaster:
    """Simple expense forecaster using linear regression"""
    
    def __init__(self, model_path: str = "models/simple_forecaster.pkl"):
        """
        Initialize the forecaster
        
        Args:
            model_path: Path to save/load the model
        """
        self.model_path = model_path
        self.model = None
        self.categories = []
        
    def prepare_data(self, transactions: List[Dict[str, Any]]) -> pd.DataFrame:
        """
        Prepare transaction data for forecasting
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            Prepared DataFrame
        """
        df = pd.DataFrame(transactions)
        
        # Convert date and ensure amount is numeric
        df['fecha'] = pd.to_datetime(df['fecha'])
        df['monto'] = pd.to_numeric(df['monto'], errors='coerce')
        
        # Group by date and category
        daily_spending = df.groupby(['fecha', 'categoria'])['monto'].sum().reset_index()
        
        # Create time series features
        daily_spending['day_of_year'] = daily_spending['fecha'].dt.dayofyear
        daily_spending['day_of_week'] = daily_spending['fecha'].dt.dayofweek
        daily_spending['month'] = daily_spending['fecha'].dt.month
        
        return daily_spending
    
    def train(self, transactions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Train the forecasting model
        
        Args:
            transactions: List of historical transactions
            
        Returns:
            Training metrics
        """
        logger.info(f"Training simple forecaster with {len(transactions)} transactions...")
        
        try:
            # Prepare data
            df = self.prepare_data(transactions)
            
            if len(df) == 0:
                raise ValueError("No valid transactions for training")
            
            self.categories = df['categoria'].unique().tolist()
            
            # Simple aggregation by day for overall trend
            daily_totals = df.groupby('fecha')['monto'].sum().reset_index()
            daily_totals['days_since_start'] = (daily_totals['fecha'] - daily_totals['fecha'].min()).dt.days
            
            if len(daily_totals) < 3:
                # Not enough data, use simple average
                self.model = {'type': 'average', 'avg_spending': daily_totals['monto'].mean()}
            else:
                # Use linear regression
                X = daily_totals[['days_since_start']].values
                y = daily_totals['monto'].values
                
                model = LinearRegression()
                model.fit(X, y)
                
                # Calculate predictions and metrics
                predictions = model.predict(X)
                mae = mean_absolute_error(y, predictions)
                rmse = np.sqrt(mean_squared_error(y, predictions))
                
                self.model = {
                    'type': 'linear',
                    'model': model,
                    'start_date': daily_totals['fecha'].min(),
                    'avg_spending': daily_totals['monto'].mean(),
                    'mae': mae,
                    'rmse': rmse
                }
            
            # Save model
            self.save_model()
            
            return {
                'status': 'success',
                'num_transactions': len(transactions),
                'num_categories': len(self.categories),
                'mae': self.model.get('mae', 0),
                'rmse': self.model.get('rmse', 0),
                'model_type': self.model['type']
            }
            
        except Exception as e:
            logger.error(f"Error training forecaster: {e}")
            return {
                'status': 'error',
                'error': str(e),
                'num_transactions': len(transactions)
            }
    
    def predict(self, days_ahead: int = 30, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Generate expense forecasts
        
        Args:
            days_ahead: Number of days to forecast
            category: Specific category to forecast (optional)
            
        Returns:
            List of forecast predictions
        """
        if not self.model:
            raise ValueError("Model not trained. Call train() first.")
        
        predictions = []
        
        try:
            if self.model['type'] == 'average':
                # Simple average prediction
                daily_avg = self.model['avg_spending']
                for i in range(days_ahead):
                    future_date = datetime.now() + timedelta(days=i+1)
                    predictions.append({
                        'date': future_date.strftime('%Y-%m-%d'),
                        'predicted_amount': daily_avg,
                        'category': category or 'Total',
                        'confidence_interval': {
                            'lower': daily_avg * 0.8,
                            'upper': daily_avg * 1.2
                        }
                    })
            
            elif self.model['type'] == 'linear':
                # Linear trend prediction
                start_date = self.model['start_date']
                linear_model = self.model['model']
                
                for i in range(days_ahead):
                    future_date = datetime.now() + timedelta(days=i+1)
                    days_since_start = (future_date - start_date).days
                    
                    predicted_amount = linear_model.predict([[days_since_start]])[0]
                    
                    # Ensure positive prediction
                    predicted_amount = max(0, predicted_amount)
                    
                    predictions.append({
                        'date': future_date.strftime('%Y-%m-%d'),
                        'predicted_amount': predicted_amount,
                        'category': category or 'Total',
                        'confidence_interval': {
                            'lower': predicted_amount * 0.7,
                            'upper': predicted_amount * 1.3
                        }
                    })
            
            logger.info(f"Generated {len(predictions)} predictions for {days_ahead} days")
            return predictions
            
        except Exception as e:
            logger.error(f"Error generating predictions: {e}")
            return []
    
    def save_model(self):
        """Save the trained model"""
        try:
            joblib.dump({
                'model': self.model,
                'categories': self.categories,
                'model_path': self.model_path
            }, self.model_path)
            logger.info(f"Simple forecaster saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")
    
    def load_model(self) -> bool:
        """
        Load a pre-trained model
        
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            data = joblib.load(self.model_path)
            self.model = data['model']
            self.categories = data['categories']
            logger.info(f"Simple forecaster loaded from {self.model_path}")
            return True
        except Exception as e:
            logger.warning(f"Could not load model from {self.model_path}: {e}")
            return False


# Alias para compatibilidad
ExpenseForecaster = SimpleExpenseForecaster
