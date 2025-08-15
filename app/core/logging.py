import sys
from loguru import logger
from app.core.config import DEBUG, UPLOAD_DIR

def setup_logging():
    
    logger.remove()
    
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level="INFO" if not DEBUG else "DEBUG",
        colorize=True
    )
    
    logger.add(
        "logs/app.log",
        rotation="10 MB",
        retention="7 days",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        level="INFO",
        compression="zip"
    )
    
    logger.info("Legal Intel Dashboard API starting up...")
    logger.info(f"Debug mode: {DEBUG}")
    logger.info(f"Upload folder: {UPLOAD_DIR}")
    
    return logger
