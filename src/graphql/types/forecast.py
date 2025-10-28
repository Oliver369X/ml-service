"""
GraphQL types for forecasts
"""
import strawberry
from typing import Optional
from datetime import datetime


@strawberry.type
class ConfidenceInterval:
    """Confidence interval for forecast"""
    lower: float
    upper: float
    confidence: float


@strawberry.type
class Forecast:
    """Expense forecast"""
    id: strawberry.ID
    user_id: strawberry.ID
    category_id: Optional[strawberry.ID]
    forecast_month: int
    forecast_year: int
    predicted_amount: float
    confidence_interval: ConfidenceInterval
    trend: str
    created_at: datetime


@strawberry.input
class GenerateForecastInput:
    """Input for generating forecasts"""
    months: int = 3
    category_id: Optional[strawberry.ID] = None

