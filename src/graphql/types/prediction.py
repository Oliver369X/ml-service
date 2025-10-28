"""
GraphQL types for predictions
"""
import strawberry
from typing import Optional, List
from datetime import datetime


@strawberry.type
class CategoryPrediction:
    """Alternative category prediction"""
    category: str
    confidence: float


@strawberry.type
class Prediction:
    """Transaction classification prediction"""
    id: strawberry.ID
    user_id: strawberry.ID
    transaction_id: Optional[strawberry.ID]
    input_text: str
    predicted_category: str
    confidence: float
    alternative_categories: Optional[List[CategoryPrediction]]
    model_version: str
    created_at: datetime


@strawberry.input
class ClassifyTransactionInput:
    """Input for classifying a transaction"""
    text: str
    amount: Optional[float] = None
    transaction_id: Optional[strawberry.ID] = None

