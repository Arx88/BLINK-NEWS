from flask import Flask
import os
import shutil
import logging # Import the logging module

from flask_cors import CORS
from .routes.api import api_bp
from .routes.topic_search import topic_search_bp # Import the new blueprint

# Configure logging
logger = logging.getLogger(__name__)

class Config:
    DEBUG = True

def create_app():
    print("--- create_app() in app.py ENTERED ---", flush=True) # Added print
    """
    Creates and configures the Flask application.
    """
    # Clear the LOG directory before app initialization
    # Corrected path to point to PROJECT_ROOT/LOG (i.e., /app/LOG)
    # os.path.dirname(os.path.abspath(__file__)) is /app/news-blink-backend/src
    # So, ../.. takes it to /app, then LOG means /app/LOG
    log_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'LOG')

    print(f"Attempting to clear LOG directory: {log_directory}", flush=True) # Added print
    try:
        if os.path.exists(log_directory):
            print(f"LOG directory exists. Proceeding to clear contents of: {log_directory}", flush=True) # Added print
            logger.info(f"Clearing LOG directory: {log_directory}")
            for item in os.listdir(log_directory):
                item_path = os.path.join(log_directory, item)
                if os.path.isfile(item_path) or os.path.islink(item_path):
                    os.unlink(item_path)
                    logger.info(f"Deleted file: {item_path}")
                elif os.path.isdir(item_path):
                    shutil.rmtree(item_path)
                    logger.info(f"Deleted directory: {item_path}")
            logger.info("LOG directory cleared successfully.")
            print("LOG directory cleared successfully via print.", flush=True) # Added print
        else:
            logger.info(f"LOG directory not found, skipping cleanup: {log_directory}")
            print(f"LOG directory NOT found at {log_directory}, skipping cleanup via print.", flush=True) # Added print
    except Exception as e:
        logger.error(f"Error clearing LOG directory: {e}", exc_info=True)
        print(f"ERROR clearing LOG directory via print: {e}", flush=True) # Added print


    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS for all routes
    CORS(app)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(topic_search_bp, url_prefix='/search') # Register the topic search blueprint

    return app

if __name__ == '__main__':
    # This is for running the app with the Flask development server.
    # For production, use a WSGI server like Gunicorn.
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)

