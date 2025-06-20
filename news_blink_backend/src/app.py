import json
import os
import logging
import logging.handlers
from flask import Flask
from flask_cors import CORS
# from routes.api import init_api # Assuming this path is correct relative to src/app.py
# from routes.topic_search import topic_search_bp # Assuming this path is correct

CONFIG_FILE_PATH = 'config.json' # This path might need adjustment if config.json is not in 'src'

def load_app_config(app):
    # Path to config.json needs to be relative to this file (src/app.py) or absolute
    # If config.json is in project root, this needs to be '../config.json'
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', CONFIG_FILE_PATH)
    if not os.path.exists(config_path):
        app.logger.error(f"Configuration file {CONFIG_FILE_PATH} not found at {config_path}!")
        return {}
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        app.logger.info(f"Configuration loaded from {config_path}")
        return config_data
    except Exception as e:
        app.logger.error(f"Error loading configuration from {config_path}: {e}")
        return {}

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    CORS(app, origins="*")

    # Configure logger for the app
    # Use app_logger from logger_config.py
    # from news_blink_backend.src.logger_config import app_logger # This will be an issue if logger_config also tries to init Flask app
    # Instead, we should configure the app.logger directly or ensure logger_config is self-contained

    # Basic configuration for Flask's built-in logger
    # The actual file handler (VoteFixLog.log) is configured in logger_config.py and used by app_logger
    # Here, we can set a basic level for Flask's default logger if needed,
    # but most logging should go through app_logger imported in other modules.

    # Example: if you want Flask's internal messages at a certain level
    # if not app.debug:
    #    app.logger.setLevel(logging.INFO)

    app_config = load_app_config(app)
    app.config['APP_CONFIG'] = app_config

    # The dedicated blink sorting warnings logger setup block has been removed.

    # Adjust import paths for init_api and topic_search_bp if they are not directly under 'routes'
    # relative to 'src' (e.g. from .routes.api import init_api)
    # Assuming routes are in news-blink-backend/src/routes/
    from .routes.api import api_bp # Corrected to import the blueprint
    from .routes.topic_search import topic_search_bp

    # If init_api was a function to register routes on app, that's different from registering a blueprint
    # The provided code had init_api(app). If api_bp is the blueprint, it should be registered.
    # Assuming api_bp is the blueprint to be registered like topic_search_bp
    app.register_blueprint(api_bp, url_prefix='/api') # Registering api_bp

    app.register_blueprint(topic_search_bp, url_prefix='/search') # Corrected url_prefix based on previous app.py
                                                                # Original subtask had /api, but old app.py had /search
                                                                # Keeping /search as it was more specific for topic_search_bp

    return app

if __name__ == '__main__':
    # This part is usually for running this specific app file directly
    # If the main entry is the root app.py, this might not be hit during normal execution
    app_instance = create_app()

    # Configure basic logging for when running directly (if not in debug mode)
    # Note: app_logger from logger_config.py should be the primary logger for app logic
    if not app_instance.debug: # Flask's default debug is False unless set
        # Basic console logging for startup messages if not in debug.
        # For production, a more robust logging setup (like what app_logger provides) is essential.
        logging.basicConfig(level=logging.INFO)
        app_instance.logger.info("Flask app running in production mode (basic console logging).")
    else:
        app_instance.logger.info("Flask app running in debug mode.")

    # Port/host settings for direct execution
    # use_reloader=False is good for some debugging scenarios, True is common for development
    app_instance.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
