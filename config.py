import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

class Config:
    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URI', 'postgresql://yashtripathi:1234@localhost:5432/book_marketplace')
    
    # Secret key for session management
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev_secret_key_change_in_production')
    
    # Microsoft OAuth settings
    MS_CLIENT_ID = os.environ.get('MS_CLIENT_ID', '')
    MS_CLIENT_SECRET = os.environ.get('MS_CLIENT_SECRET', '')
    MS_REDIRECT_URI = os.environ.get('MS_REDIRECT_URI', 'http://localhost:5000/auth/callback')
    MS_AUTHORITY = 'https://login.microsoftonline.com/common'
    MS_SCOPE = ['User.Read', 'email']
    
    # Upload settings
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB