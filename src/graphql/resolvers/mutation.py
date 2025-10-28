"""
GraphQL Mutations
"""
import strawberry
from strawberry.types import Info
from typing import List
from datetime import datetime, timedelta
import uuid
import httpx

from ..types import (
    Prediction,
    CategoryPrediction,
    ClassifyTransactionInput,
    Forecast,
    GenerateForecastInput,
    SpendingPattern,
    AnalyzePatternsInput
)
from ..context import Context
from ...database.models import MLPrediction, Forecast as ForecastModel, SpendingPattern as PatternModel
from ...ml import TransactionClassifier, ExpenseForecaster
from ...dl import PatternAnalyzer
from ...config import get_settings
from ...utils.logger import logger

settings = get_settings()

# Initialize ML models
classifier = TransactionClassifier()
forecaster = ExpenseForecaster()
pattern_analyzer = PatternAnalyzer()


@strawberry.type
class Mutation:
    """GraphQL Mutations"""
    
    @strawberry.mutation
    async def classify_transaction(
        self,
        info: Info[Context, None],
        input: ClassifyTransactionInput
    ) -> Prediction:
        """
        Classify a transaction into a category
        
        Args:
            input: Classification input
            
        Returns:
            Prediction result
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        logger.info(f"Classifying transaction for user {context.user_id}: {input.text}")
        
        # Predict category
        predictions = classifier.predict(input.text, top_k=3)
        
        # Main prediction
        main_pred = predictions[0]
        alternatives = predictions[1:] if len(predictions) > 1 else []
        
        # Save to database
        prediction = MLPrediction(
            user_id=uuid.UUID(context.user_id),
            transaction_id=uuid.UUID(input.transaction_id) if input.transaction_id else None,
            input_text=input.text,
            predicted_category=main_pred['category'],
            confidence=main_pred['confidence'],
            alternative_categories=alternatives,
            model_version=settings.ml_model_version
        )
        
        context.db.add(prediction)
        context.db.commit()
        context.db.refresh(prediction)
        
        return Prediction(
            id=str(prediction.id),
            user_id=str(prediction.user_id),
            transaction_id=str(prediction.transaction_id) if prediction.transaction_id else None,
            input_text=prediction.input_text,
            predicted_category=prediction.predicted_category,
            confidence=prediction.confidence,
            alternative_categories=[
                CategoryPrediction(
                    category=alt['category'],
                    confidence=alt['confidence']
                )
                for alt in alternatives
            ],
            model_version=prediction.model_version,
            created_at=prediction.created_at
        )
    
    @strawberry.mutation
    async def generate_forecast(
        self,
        info: Info[Context, None],
        input: GenerateForecastInput
    ) -> List[Forecast]:
        """
        Generate expense forecasts
        
        Args:
            input: Forecast parameters
            
        Returns:
            List of forecasts
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        logger.info(f"Generating {input.months} month forecast for user {context.user_id}")
        
        # Fetch historical transactions from expenses service
        transactions = await self._fetch_user_transactions(context.user_id)
        
        if not transactions:
            raise Exception("No transaction history found. Cannot generate forecast.")
        
        # Generate forecasts
        try:
            monthly_forecasts = forecaster.forecast_by_month(months=input.months)
        except Exception as e:
            logger.error(f"Error generating forecast: {e}")
            # Use default forecast if model fails
            monthly_forecasts = forecaster._forecast_default(input.months * 30)
            monthly_forecasts = self._aggregate_to_monthly(monthly_forecasts, input.months)
        
        # Save to database
        saved_forecasts = []
        for forecast_data in monthly_forecasts:
            forecast = ForecastModel(
                user_id=uuid.UUID(context.user_id),
                category_id=uuid.UUID(input.category_id) if input.category_id else None,
                forecast_month=forecast_data['month'],
                forecast_year=forecast_data['year'],
                predicted_amount=forecast_data['predicted_amount'],
                confidence_lower=forecast_data.get('lower_bound', 0),
                confidence_upper=forecast_data.get('upper_bound', 0),
                confidence_level=forecast_data.get('confidence', 0.95),
                trend=forecast_data.get('trend', 'stable')
            )
            
            context.db.merge(forecast)  # Use merge to handle duplicates
            saved_forecasts.append(forecast)
        
        context.db.commit()
        
        from ..types.forecast import ConfidenceInterval
        
        return [
            Forecast(
                id=str(f.id),
                user_id=str(f.user_id),
                category_id=str(f.category_id) if f.category_id else None,
                forecast_month=f.forecast_month,
                forecast_year=f.forecast_year,
                predicted_amount=float(f.predicted_amount),
                confidence_interval=ConfidenceInterval(
                    lower=float(f.confidence_lower or 0),
                    upper=float(f.confidence_upper or 0),
                    confidence=f.confidence_level or 0.95
                ),
                trend=f.trend or 'stable',
                created_at=f.created_at
            )
            for f in saved_forecasts
        ]
    
    @strawberry.mutation
    async def analyze_patterns(
        self,
        info: Info[Context, None],
        input: AnalyzePatternsInput
    ) -> SpendingPattern:
        """
        Analyze spending patterns
        
        Args:
            input: Analysis parameters
            
        Returns:
            Pattern analysis result
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        logger.info(f"Analyzing spending patterns for user {context.user_id}")
        
        # Fetch historical transactions
        transactions = await self._fetch_user_transactions(
            context.user_id,
            months=input.months
        )
        
        if not transactions:
            raise Exception("No transaction history found for pattern analysis.")
        
        # Analyze patterns
        analysis = pattern_analyzer.analyze_patterns(transactions)
        
        # Calculate date range
        end_date = input.end_date or datetime.now()
        start_date = input.start_date or (end_date - timedelta(days=input.months * 30))
        
        # Save to database
        pattern = PatternModel(
            user_id=uuid.UUID(context.user_id),
            pattern_type=analysis['pattern_type'],
            pattern_data={
                'patterns': analysis['patterns'],
                'stability_score': analysis['stability_score'],
                'unusual_days': analysis['unusual_days']
            },
            insights={'insights': analysis['insights']},
            start_date=start_date.date(),
            end_date=end_date.date()
        )
        
        context.db.add(pattern)
        context.db.commit()
        context.db.refresh(pattern)
        
        from ..types.pattern import Pattern, Insight
        
        return SpendingPattern(
            user_id=str(pattern.user_id),
            pattern_type=pattern.pattern_type,
            patterns=[
                Pattern(
                    type=p['type'],
                    description=p['description'],
                    impact=p['impact']
                )
                for p in analysis['patterns']
            ],
            insights=[
                Insight(
                    category=i['category'],
                    message=i['message'],
                    severity=i['severity']
                )
                for i in analysis['insights']
            ],
            stability_score=analysis['stability_score'],
            unusual_days=analysis['unusual_days'],
            analyzed_at=pattern.created_at
        )
    
    async def _fetch_user_transactions(
        self,
        user_id: str,
        months: int = 6
    ) -> List[dict]:
        """
        Fetch user transactions from expenses service
        
        Args:
            user_id: User ID
            months: Number of months of history
            
        Returns:
            List of transactions
        """
        # TODO: Implement actual GraphQL call to expenses service
        # For now, return mock data
        logger.warning("Using mock transaction data. Implement expenses service integration.")
        
        # Mock data for testing
        from datetime import timedelta
        import random
        
        transactions = []
        start_date = datetime.now() - timedelta(days=months * 30)
        
        for i in range(months * 30):
            date = start_date + timedelta(days=i)
            
            # Random transactions
            if random.random() > 0.3:  # 70% chance of transaction per day
                transactions.append({
                    'id': str(uuid.uuid4()),
                    'user_id': user_id,
                    'amount': random.uniform(10, 200),
                    'date': date.isoformat(),
                    'category': random.choice(['Food', 'Transport', 'Bills', 'Entertainment']),
                    'description': 'Transaction ' + str(i)
                })
        
        return transactions
    
    def _aggregate_to_monthly(self, daily_forecasts: List[dict], months: int) -> List[dict]:
        """Aggregate daily forecasts to monthly"""
        # Simple aggregation for default forecasts
        import pandas as pd
        
        df = pd.DataFrame(daily_forecasts)
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.month
        df['year'] = df['date'].dt.year
        
        monthly = df.groupby(['year', 'month']).agg({
            'predicted_amount': 'sum',
            'lower_bound': 'sum',
            'upper_bound': 'sum'
        }).reset_index()
        
        return [
            {
                'month': int(row['month']),
                'year': int(row['year']),
                'predicted_amount': float(row['predicted_amount']),
                'lower_bound': float(row['lower_bound']),
                'upper_bound': float(row['upper_bound']),
                'confidence': 0.95,
                'trend': 'stable'
            }
            for _, row in monthly.head(months).iterrows()
        ]

