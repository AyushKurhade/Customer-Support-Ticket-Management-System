import os
from pathlib import Path
from dotenv import load_dotenv

# Base directory of the project
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Load .env file from project root
load_dotenv(BASE_DIR / '.env', override=True)

class Config:
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_PORT = int(os.getenv('DB_PORT', 3306))
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', '')
    DB_NAME = os.getenv('DB_NAME', 'support_ticket_db')
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-dev-secret-key')
    FLASK_ENV = os.getenv('FLASK_ENV', 'development')

