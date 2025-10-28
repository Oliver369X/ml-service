"""
GraphQL types for pattern analysis
"""
import strawberry
from typing import List, Optional
from datetime import datetime


@strawberry.type
class Pattern:
    """Detected spending pattern"""
    type: str
    description: str
    impact: str


@strawberry.type
class Insight:
    """Financial insight"""
    category: str
    message: str
    severity: str


@strawberry.type
class SpendingPattern:
    """Spending pattern analysis result"""
    user_id: strawberry.ID
    pattern_type: str
    patterns: List[Pattern]
    insights: List[Insight]
    stability_score: float
    unusual_days: int
    analyzed_at: datetime


@strawberry.input
class AnalyzePatternsInput:
    """Input for pattern analysis"""
    months: int = 6
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None

