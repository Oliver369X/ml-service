"""
Configuration settings for ML Service
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings"""
    
    # Server
    port: int = 5015
    env: str = "development"
    
    # Database
    database_url: str = "postgresql://mluser:mlpassword@localhost:5433/mldb"
    
    # JWT
    jwt_secret: str = "WERWRWERWERW"
    
    # External Services
    expenses_service_url: str = "http://localhost:5010"
    
    # ML Models
    ml_model_version: str = "1.0.0"  # Renombrado para evitar conflicto con 'model_'
    min_confidence_threshold: float = 0.6
    classifier_model_path: str = "models/transaction_classifier.pkl"
    forecaster_model_path: str = "models/expense_forecaster.pkl"
    pattern_model_path: str = "models/pattern_analyzer.h5"
    
    # Logging
    log_level: str = "INFO"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",  # Ignorar variables extra del .env
        protected_namespaces=('settings_',)  # Cambiar namespace protegido
    )


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance"""
    return Settings()

