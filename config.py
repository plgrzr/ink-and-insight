import os
from dotenv import load_dotenv

# Add debug prints
print("Current working directory:", os.getcwd())
print("Loading .env file...")
load_dotenv()
print("Environment variables after loading .env:")
print("MATHPIX_APP_ID:", os.getenv('MATHPIX_APP_ID'))
print("MATHPIX_APP_KEY:", os.getenv('MATHPIX_APP_KEY')[:10] + "..." if os.getenv('MATHPIX_APP_KEY') else None)
print("GOOGLE_CLOUD_API_KEY:", os.getenv('GOOGLE_CLOUD_API_KEY')[:10] + "..." if os.getenv('GOOGLE_CLOUD_API_KEY') else None)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here'
    UPLOAD_FOLDER = 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB max file size
    
    # API Keys
    MATHPIX_APP_ID = os.environ.get('MATHPIX_APP_ID')
    MATHPIX_APP_KEY = os.environ.get('MATHPIX_APP_KEY')
    GOOGLE_CLOUD_API_KEY = os.environ.get('GOOGLE_CLOUD_API_KEY')