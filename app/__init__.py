from flask import Flask
from config import Config
import os
from flask_cors import CORS

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app)
    
    # Set additional security headers
    @app.after_request
    def add_security_headers(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    # Print environment variables for debugging
    print("\nEnvironment variables:")
    print(f"MATHPIX_APP_ID: {app.config.get('MATHPIX_APP_ID', 'Not set')}")
    
    mathpix_key = app.config.get('MATHPIX_APP_KEY', '')
    print(f"MATHPIX_APP_KEY: {mathpix_key[:10] + '...' if mathpix_key else 'Not set'}")
    
    google_key = app.config.get('GOOGLE_CLOUD_API_KEY', '')
    print(f"GOOGLE_CLOUD_API_KEY: {google_key[:10] + '...' if google_key else 'Not set'}")
    print(f"Full Google Cloud API Key length: {len(google_key) if google_key else 0}")
    print(f"Environment variable directly: {os.getenv('GOOGLE_CLOUD_API_KEY')}")

    # Ensure upload and reports directories exist
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs('reports', exist_ok=True)

    # Register blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app 