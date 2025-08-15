import os
from typing import Optional, List

from dotenv import load_dotenv
load_dotenv()

# JWT Settings
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-this-in-production')
ALGORITHM = os.getenv('ALGORITHM', 'HS256')
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '30'))

# Database Settings
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///./legal_dashboard.db')

# File Storage Settings
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')

# Server Settings
HOST = os.getenv('HOST', '0.0.0.0')
PORT = int(os.getenv('PORT', '8000'))
DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'

# CORS Settings
ALLOWED_ORIGINS_STR = os.getenv('ALLOWED_ORIGINS', 'http://localhost:3000,http://127.0.0.1:3000')
ALLOWED_ORIGINS = ALLOWED_ORIGINS_STR.split(',')

# API Settings
API_TITLE = os.getenv('API_TITLE', 'Legal Intel Dashboard API')
API_VERSION = os.getenv('API_VERSION', '1.3.0')

# File Processing Settings
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', str(50 * 1024 * 1024)))  # 50MB
ALLOWED_FILE_TYPES_STR = os.getenv('ALLOWED_FILE_TYPES', '.pdf,.docx,.doc')
ALLOWED_FILE_TYPES = ALLOWED_FILE_TYPES_STR.split(',')
MAX_DOCUMENT_SIZE = int(os.getenv('MAX_DOCUMENT_SIZE', str(10 * 1024 * 1024)))  # 10MB

# # Debug: Print loaded environment variables
# print(f"Loaded SECRET_KEY: {SECRET_KEY}")
# print(f"Loaded HOST: {HOST}")
# print(f"Loaded PORT: {PORT}")
# print(f"Loaded DEBUG: {DEBUG}")
# print(f"Loaded UPLOAD_DIR: {UPLOAD_DIR}")
# print(f"Loaded ALLOWED_ORIGINS: {ALLOWED_ORIGINS}")

# Create uploads directory
os.makedirs(UPLOAD_DIR, exist_ok=True)