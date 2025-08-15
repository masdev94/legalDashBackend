import sys
from loguru import logger
from app.core.config import settings

def setup_logging():
    
    # Remove default logger
    logger.remove()
    
    # Add console logger
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not settings.debug else "DEBUG",
        colorize=True
    )
    
    # Add file logger
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        compression="zip"
    )
    
    # Log application startup
    logger.info("Legal Intel Dashboard API starting up...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Upload folder: {settings.upload_folder}")
    
    return logger
