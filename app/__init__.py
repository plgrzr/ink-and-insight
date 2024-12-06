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

    # Ensure required directories exist with proper permissions
    for directory in ['uploads', 'reports']:
        dir_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), directory)
        os.makedirs(dir_path, exist_ok=True)
        # Ensure directory is writable
        os.chmod(dir_path, 0o755)
        app.config[f'{directory.upper()}_FOLDER'] = dir_path

    # Register blueprint
    from app.routes import main
    app.register_blueprint(main)

    return app 