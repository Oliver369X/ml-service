"""
Expense Forecaster using Prophet for time series prediction
Predicts future expenses based on historical data
"""
import pickle
import os
from typing import List, Dict
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from prophet import Prophet
from prophet.diagnostics import cross_validation, performance_metrics

from ..config import get_settings
from ..utils.logger import logger

settings = get_settings()


class ExpenseForecaster:
    """
    Predictor de gastos futuros usando Prophet (Facebook)
    """
    
    def __init__(self, model_path: str = None):
        """
        Initialize forecaster
        
        Args:
            model_path: Path to saved model file
        """
        self.model_path = model_path or settings.forecaster_model_path
        self.model = None
        self.is_trained = False
        
        # Cargar modelo si existe
        if os.path.exists(self.model_path):
            self.load_model()
    
    def prepare_data(self, transactions: List[Dict]) -> pd.DataFrame:
        """
        Prepare transaction data for Prophet
        
        Prophet requires columns: 'ds' (date) and 'y' (value)
        
        Args:
            transactions: List of transaction dictionaries
            
        Returns:
            DataFrame ready for Prophet
        """
        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        
        # Ensure date column is datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Aggregate by day (sum of expenses)
        daily_expenses = df.groupby('date')['amount'].sum().reset_index()
        
        # Rename columns for Prophet
        daily_expenses.columns = ['ds', 'y']
        
        # Fill missing dates with 0
        date_range = pd.date_range(
            start=daily_expenses['ds'].min(),
            end=daily_expenses['ds'].max(),
            freq='D'
        )
        daily_expenses = daily_expenses.set_index('ds').reindex(date_range, fill_value=0).reset_index()
        daily_expenses.columns = ['ds', 'y']
        
        return daily_expenses
    
    def train(self, transactions: List[Dict]) -> Dict:
        """
        Train the forecaster
        
        Args:
            transactions: List of historical transactions
            
        Returns:
            Training metrics
        """
        logger.info(f"Training forecaster with {len(transactions)} transactions...")
        
        # Prepare data
        df = self.prepare_data(transactions)
        
        # Initialize Prophet model
        self.model = Prophet(
            daily_seasonality=True,
            weekly_seasonality=True,
            yearly_seasonality=True,
            seasonality_mode='multiplicative',
            changepoint_prior_scale=0.05
        )
        
        # Train model
        self.model.fit(df)
        self.is_trained = True
        
        # Cross-validation for metrics (últimos 30 días)
        try:
            df_cv = cross_validation(
                self.model,
                initial='30 days',
                period='7 days',
                horizon='7 days'
            )
            metrics = performance_metrics(df_cv)
            mape = metrics['mape'].mean()
            rmse = metrics['rmse'].mean()
        except Exception as e:
            logger.warning(f"Could not calculate metrics: {e}")
            mape = None
            rmse = None
        
        # Save model
        self.save_model()
        
        logger.info(f"Forecaster trained successfully")
        
        return {
            'num_samples': len(transactions),
            'date_range': {
                'start': df['ds'].min().isoformat(),
                'end': df['ds'].max().isoformat()
            },
            'mape': float(mape) if mape else None,
            'rmse': float(rmse) if rmse else None
        }
    
    def forecast(
        self,
        periods: int = 30,
        frequency: str = 'D'
    ) -> List[Dict]:
        """
        Generate forecast
        
        Args:
            periods: Number of periods to forecast
            frequency: Frequency ('D' for daily, 'M' for monthly)
            
        Returns:
            List of forecasts
        """
        if not self.is_trained:
            logger.warning("Forecaster not trained. Returning default forecast.")
            return self._forecast_default(periods)
        
        # Create future dataframe
        future = self.model.make_future_dataframe(periods=periods, freq=frequency)
        
        # Predict
        forecast_df = self.model.predict(future)
        
        # Get only future predictions
        forecast_df = forecast_df.tail(periods)
        
        # Convert to list of dicts
        forecasts = []
        for _, row in forecast_df.iterrows():
            forecasts.append({
                'date': row['ds'].isoformat(),
                'predicted_amount': float(max(row['yhat'], 0)),  # No negative predictions
                'lower_bound': float(max(row['yhat_lower'], 0)),
                'upper_bound': float(max(row['yhat_upper'], 0)),
                'confidence': 0.95
            })
        
        return forecasts
    
    def forecast_by_month(self, months: int = 3) -> List[Dict]:
        """
        Generate monthly forecasts
        
        Args:
            months: Number of months to forecast
            
        Returns:
            List of monthly forecasts
        """
        # Get daily forecasts for the period
        days = months * 30
        daily_forecasts = self.forecast(periods=days, frequency='D')
        
        # Convert to DataFrame
        df = pd.DataFrame(daily_forecasts)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        # Aggregate by month
        monthly = df.groupby(['year', 'month']).agg({
            'predicted_amount': 'sum',
            'lower_bound': 'sum',
            'upper_bound': 'sum'
        }).reset_index()
        
        # Determine trend
        amounts = monthly['predicted_amount'].values
        if len(amounts) > 1:
            trend = 'increasing' if amounts[-1] > amounts[0] else 'decreasing'
        else:
            trend = 'stable'
        
        # Convert to list
        forecasts = []
        for _, row in monthly.iterrows():
            forecasts.append({
                'month': int(row['month']),
                'year': int(row['year']),
                'predicted_amount': float(row['predicted_amount']),
                'lower_bound': float(row['lower_bound']),
                'upper_bound': float(row['upper_bound']),
                'confidence': 0.95,
                'trend': trend
            })
        
        return forecasts
    
    def _forecast_default(self, periods: int) -> List[Dict]:
        """
        Default forecast when model is not trained
        
        Args:
            periods: Number of periods
            
        Returns:
            Default forecasts
        """
        forecasts = []
        base_amount = 100.0  # Default daily expense
        
        for i in range(periods):
            date = datetime.now() + timedelta(days=i)
            
            forecasts.append({
                'date': date.isoformat(),
                'predicted_amount': base_amount,
                'lower_bound': base_amount * 0.8,
                'upper_bound': base_amount * 1.2,
                'confidence': 0.5
            })
        
        return forecasts
    
    def save_model(self):
        """Save model to disk"""
        if not self.model:
            logger.warning("No model to save")
            return
        
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        
        with open(self.model_path, 'wb') as f:
            pickle.dump({
                'model': self.model,
                'is_trained': self.is_trained
            }, f)
        
        logger.info(f"Forecaster saved to {self.model_path}")
    
    def load_model(self):
        """Load model from disk"""
        try:
            with open(self.model_path, 'rb') as f:
                data = pickle.load(f)
            
            self.model = data['model']
            self.is_trained = data.get('is_trained', True)
            
            logger.info(f"Forecaster loaded from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading forecaster: {e}")
            self.is_trained = False

