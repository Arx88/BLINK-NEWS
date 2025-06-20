import os # Ensure os is imported for os.getcwd(), os.listdir()
import sys # Ensure sys is imported for sys.path
print(f"DEBUG: Current working directory: {os.getcwd()}", flush=True)
# 'added_path' was related to the removed sys.path.insert, so we'll use os.getcwd() or a relevant path
# For listing, let's list the current working directory.
current_dir_to_list = os.getcwd() # Or use os.path.abspath(os.path.dirname(__file__)) if that's more relevant
print(f"DEBUG: Path whose contents will be listed: {current_dir_to_list}", flush=True)
print(f"DEBUG: sys.path at startup: {sys.path}", flush=True)
try:
    print(f"DEBUG: Listing contents of '{current_dir_to_list}': {os.listdir(current_dir_to_list)}", flush=True)
except Exception as e:
    print(f"DEBUG: Error listing contents of '{current_dir_to_list}': {e}", flush=True)

import json
# import os # os is already imported above for the diagnostic block
import logging
import logging.handlers
from flask import Flask
from flask_cors import CORS
# news_blink_backend.src.logger_config should be found if app.py is run from project root
# and news-blink-backend has __init__.py , and src has __init__.py
from news_blink_backend.src.logger_config import app_logger as configured_app_logger
from routes.api import init_api # This import assumes 'routes' is a top-level directory or findable via sys.path
from routes.topic_search import topic_search_bp # Same assumption for this

CONFIG_FILE_PATH = 'config.json'

def load_app_config(app):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_PATH)
    if not os.path.exists(config_path):
        app.logger.error(f"Configuration file {CONFIG_FILE_PATH} not found at {config_path}!")
        # For now, we'll proceed with empty config if file not found,
        # but a real app might raise an error or use hardcoded defaults.
        # Or, ensure config.json is always present.
        return {}
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        app.logger.info(f"Configuration loaded from {config_path}")
        return config_data
    except Exception as e:
        app.logger.error(f"Error loading configuration from {config_path}: {e}")
        return {} # Return empty or default config on error

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    CORS(app, origins="*")  # Habilitar CORS para permitir solicitudes desde el frontend

    # Integrate configured_app_logger into Flask's app.logger
    # Remove Flask's default handlers
    for handler in list(app.logger.handlers):
        app.logger.removeHandler(handler)
    # Add handlers from our configured_app_logger
    for handler in configured_app_logger.handlers:
        app.logger.addHandler(handler)
    # Set Flask's app.logger level to match our configured_app_logger's level
    app.logger.setLevel(configured_app_logger.level)
    # Prevent Flask's app.logger from propagating to the root logger,
    # as we've explicitly set its handlers from configured_app_logger.
    app.logger.propagate = False

    app.logger.info("Root app.logger configured to use handlers from configured_app_logger (VoteFixLog.log).")

    # Cargar configuración de la aplicación
    app_config = load_app_config(app)
    app.config['APP_CONFIG'] = app_config
    
    # Inicializar las rutas de la API
    init_api(app)
    
    # Registrar las nuevas rutas de búsqueda por tema
    app.register_blueprint(topic_search_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    # Ensure the app context is available for logging, etc.
    app_instance = create_app()
    # The logger is configured by Flask. If running standalone, need to configure logging.
    # For example, if not in debug or if run directly via python app.py without Flask CLI:
    # if not app_instance.debug: # Removed: logging.basicConfig
    #     import logging

    app_instance.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

