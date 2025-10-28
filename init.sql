-- Database initialization script
-- This runs automatically when the container starts for the first time

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create tables
CREATE TABLE IF NOT EXISTS ml_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    transaction_id UUID,
    input_text TEXT NOT NULL,
    predicted_category VARCHAR(100) NOT NULL,
    confidence FLOAT NOT NULL,
    alternative_categories JSONB,
    model_version VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT check_confidence CHECK (confidence >= 0 AND confidence <= 1)
);

CREATE INDEX idx_user_predictions ON ml_predictions(user_id, created_at DESC);
CREATE INDEX idx_transaction ON ml_predictions(transaction_id);

-- Forecasts table
CREATE TABLE IF NOT EXISTS forecasts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    category_id UUID,
    forecast_month INT NOT NULL,
    forecast_year INT NOT NULL,
    predicted_amount DECIMAL(10,2) NOT NULL,
    confidence_lower DECIMAL(10,2),
    confidence_upper DECIMAL(10,2),
    confidence_level FLOAT DEFAULT 0.95,
    trend VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW(),
    
    CONSTRAINT check_month CHECK (forecast_month >= 1 AND forecast_month <= 12),
    CONSTRAINT check_year CHECK (forecast_year >= 2000)
);

CREATE INDEX idx_user_forecasts ON forecasts(user_id, forecast_year, forecast_month);
CREATE UNIQUE INDEX idx_unique_forecast ON forecasts(user_id, category_id, forecast_year, forecast_month);

-- Patterns table
CREATE TABLE IF NOT EXISTS spending_patterns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL,
    pattern_type VARCHAR(50) NOT NULL,
    pattern_data JSONB NOT NULL,
    insights JSONB,
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_user_patterns ON spending_patterns(user_id, created_at DESC);

-- Training feedback for continuous improvement
CREATE TABLE IF NOT EXISTS training_feedback (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID REFERENCES ml_predictions(id),
    user_id UUID NOT NULL,
    correct_category VARCHAR(100),
    was_helpful BOOLEAN,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_feedback_predictions ON training_feedback(prediction_id);

-- Model metadata
CREATE TABLE IF NOT EXISTS model_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    version VARCHAR(50) NOT NULL,
    accuracy FLOAT,
    trained_at TIMESTAMP NOT NULL,
    training_data_size INT,
    hyperparameters JSONB,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_active_models ON model_metadata(model_name, is_active);

-- Insert initial model metadata
INSERT INTO model_metadata (model_name, model_type, version, trained_at, is_active) VALUES
('transaction_classifier', 'CLASSIFIER', '1.0.0', NOW(), TRUE),
('expense_forecaster', 'FORECASTER', '1.0.0', NOW(), TRUE),
('pattern_analyzer', 'PATTERN_ANALYZER', '1.0.0', NOW(), TRUE);

