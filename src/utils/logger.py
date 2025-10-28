"""
Logging configuration
"""
import logging
import sys
from pythonjsonlogger import jsonlogger

from ..config import get_settings

settings = get_settings()


def setup_logger(name: str) -> logging.Logger:
    """
    Setup logger with JSON formatting
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger
    """
    logger = logging.getLogger(name)
    
    # Ensure valid log level
    log_level = settings.log_level.upper()
    valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if log_level not in valid_levels:
        log_level = 'INFO'  # Default to INFO if invalid
    
    logger.setLevel(getattr(logging, log_level))
    
    # Console handler
    handler = logging.StreamHandler(sys.stdout)
    
    # JSON formatter (simplificado para evitar errores)
    formatter = jsonlogger.JsonFormatter(
        '%(asctime)s %(levelname)s %(name)s %(message)s'
    )
    handler.setFormatter(formatter)
    
    logger.addHandler(handler)
    
    return logger


# Default logger
logger = setup_logger('ml_service')

