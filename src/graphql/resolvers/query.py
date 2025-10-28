"""
GraphQL Queries
"""
import strawberry
from strawberry.types import Info
from typing import List, Optional
from datetime import datetime, timedelta
import uuid

from ..types import Prediction, Forecast, SpendingPattern
from ..context import Context
from ...database.models import MLPrediction, Forecast as ForecastModel, SpendingPattern as PatternModel
from ...utils.logger import logger


@strawberry.type
class Query:
    """GraphQL Queries"""
    
    @strawberry.field
    def predictions(
        self,
        info: Info[Context, None],
        limit: int = 100,
        offset: int = 0
    ) -> List[Prediction]:
        """
        Get user's predictions
        
        Args:
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of predictions
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        # Query database
        predictions = context.db.query(MLPrediction).filter(
            MLPrediction.user_id == uuid.UUID(context.user_id)
        ).order_by(
            MLPrediction.created_at.desc()
        ).limit(limit).offset(offset).all()
        
        # Convert to GraphQL type
        return [
            Prediction(
                id=str(p.id),
                user_id=str(p.user_id),
                transaction_id=str(p.transaction_id) if p.transaction_id else None,
                input_text=p.input_text,
                predicted_category=p.predicted_category,
                confidence=p.confidence,
                alternative_categories=p.alternative_categories,
                model_version=p.model_version,
                created_at=p.created_at
            )
            for p in predictions
        ]
    
    @strawberry.field
    def prediction(
        self,
        info: Info[Context, None],
        id: strawberry.ID
    ) -> Optional[Prediction]:
        """
        Get a specific prediction
        
        Args:
            id: Prediction ID
            
        Returns:
            Prediction or None
        """
        context: Context = info.context
        
        prediction = context.db.query(MLPrediction).filter(
            MLPrediction.id == uuid.UUID(id)
        ).first()
        
        if not prediction:
            return None
        
        return Prediction(
            id=str(prediction.id),
            user_id=str(prediction.user_id),
            transaction_id=str(prediction.transaction_id) if prediction.transaction_id else None,
            input_text=prediction.input_text,
            predicted_category=prediction.predicted_category,
            confidence=prediction.confidence,
            alternative_categories=prediction.alternative_categories,
            model_version=prediction.model_version,
            created_at=prediction.created_at
        )
    
    @strawberry.field
    def forecasts(
        self,
        info: Info[Context, None],
        category_id: Optional[strawberry.ID] = None
    ) -> List[Forecast]:
        """
        Get user's forecasts
        
        Args:
            category_id: Optional category filter
            
        Returns:
            List of forecasts
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        query = context.db.query(ForecastModel).filter(
            ForecastModel.user_id == uuid.UUID(context.user_id)
        )
        
        if category_id:
            query = query.filter(ForecastModel.category_id == uuid.UUID(category_id))
        
        forecasts = query.order_by(
            ForecastModel.forecast_year.desc(),
            ForecastModel.forecast_month.desc()
        ).all()
        
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
            for f in forecasts
        ]
    
    @strawberry.field
    def latest_pattern_analysis(
        self,
        info: Info[Context, None]
    ) -> Optional[SpendingPattern]:
        """
        Get user's latest pattern analysis
        
        Returns:
            Latest spending pattern analysis
        """
        context: Context = info.context
        
        if not context.user_id:
            raise Exception("User not authenticated")
        
        pattern = context.db.query(PatternModel).filter(
            PatternModel.user_id == uuid.UUID(context.user_id)
        ).order_by(
            PatternModel.created_at.desc()
        ).first()
        
        if not pattern:
            return None
        
        from ..types.pattern import Pattern, Insight
        
        # Parse pattern data
        patterns_data = pattern.pattern_data.get('patterns', [])
        insights_data = pattern.insights.get('insights', []) if pattern.insights else []
        
        return SpendingPattern(
            user_id=str(pattern.user_id),
            pattern_type=pattern.pattern_type,
            patterns=[
                Pattern(
                    type=p.get('type', ''),
                    description=p.get('description', ''),
                    impact=p.get('impact', '')
                )
                for p in patterns_data
            ],
            insights=[
                Insight(
                    category=i.get('category', ''),
                    message=i.get('message', ''),
                    severity=i.get('severity', 'INFO')
                )
                for i in insights_data
            ],
            stability_score=pattern.pattern_data.get('stability_score', 0.5),
            unusual_days=pattern.pattern_data.get('unusual_days', 0),
            analyzed_at=pattern.created_at
        )

