
import json
import os
import logging
import logging.handlers
from flask import Flask
from flask_cors import CORS
from news_blink_backend.src.logger_config import app_logger as configured_app_logger
from routes.api import init_api
from routes.topic_search import topic_search_bp

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

