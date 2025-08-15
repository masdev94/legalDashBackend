from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    
    api_title: str = "Legal Intel Dashboard API"
    api_version: str = "1.0.0"
    debug: bool = False
    
    host: str = "0.0.0.0"
    port: int = 8000
    
    allowed_origins: list = ["http://localhost:3000"]
    
    max_file_size: int = 50 * 1024 * 1024  # 50MB
    allowed_file_types: list = [".pdf", ".docx", ".doc"]
    upload_folder: str = "uploads"
    
    max_document_size: int = 10 * 1024 * 1024  
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

os.makedirs(settings.upload_folder, exist_ok=True)