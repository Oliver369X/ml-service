"""
SQLAlchemy models for ML Service
"""
from sqlalchemy import (
    Column, String, Float, Integer, Boolean, 
    DateTime, Date, Text, ForeignKey, DECIMAL, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
import uuid

from .connection import Base


class MLPrediction(Base):
    """ML Predictions for transaction classification"""
    __tablename__ = 'ml_predictions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    transaction_id = Column(UUID(as_uuid=True), nullable=True)
    input_text = Column(Text, nullable=False)
    predicted_category = Column(String(100), nullable=False)
    confidence = Column(Float, nullable=False)
    alternative_categories = Column(JSONB, nullable=True)
    model_version = Column(String(50), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    
    __table_args__ = (
        CheckConstraint('confidence >= 0 AND confidence <= 1', name='check_confidence'),
    )


class Forecast(Base):
    """Expense forecasts"""
    __tablename__ = 'forecasts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    category_id = Column(UUID(as_uuid=True), nullable=True)
    forecast_month = Column(Integer, nullable=False)
    forecast_year = Column(Integer, nullable=False)
    predicted_amount = Column(DECIMAL(10, 2), nullable=False)
    confidence_lower = Column(DECIMAL(10, 2), nullable=True)
    confidence_upper = Column(DECIMAL(10, 2), nullable=True)
    confidence_level = Column(Float, default=0.95)
    trend = Column(String(20), nullable=True)  # 'increasing', 'decreasing', 'stable'
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    __table_args__ = (
        CheckConstraint('forecast_month >= 1 AND forecast_month <= 12', name='check_month'),
        CheckConstraint('forecast_year >= 2000', name='check_year'),
    )


class SpendingPattern(Base):
    """Detected spending patterns"""
    __tablename__ = 'spending_patterns'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    pattern_type = Column(String(50), nullable=False)
    pattern_data = Column(JSONB, nullable=False)
    insights = Column(JSONB, nullable=True)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class TrainingFeedback(Base):
    """User feedback for model improvement"""
    __tablename__ = 'training_feedback'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prediction_id = Column(UUID(as_uuid=True), ForeignKey('ml_predictions.id'), nullable=True)
    user_id = Column(UUID(as_uuid=True), nullable=False)
    correct_category = Column(String(100), nullable=True)
    was_helpful = Column(Boolean, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ModelMetadata(Base):
    """ML Model metadata"""
    __tablename__ = 'model_metadata'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    model_type = Column(String(50), nullable=False)
    version = Column(String(50), nullable=False)
    accuracy = Column(Float, nullable=True)
    trained_at = Column(DateTime(timezone=True), nullable=False)
    training_data_size = Column(Integer, nullable=True)
    hyperparameters = Column(JSONB, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

