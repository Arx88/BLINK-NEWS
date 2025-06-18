
import json
import os
import logging
import logging.handlers
from flask import Flask
from flask_cors import CORS
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

    # Cargar configuración de la aplicación
    app_config = load_app_config(app)
    app.config['APP_CONFIG'] = app_config

    # --- Setup for dedicated blink sorting warnings logger ---
    LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'LOG')
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    warnings_log_file = os.path.join(LOG_DIR, 'blink_sorting_warnings.log')

    # Create a specific logger
    warnings_logger = logging.getLogger('blink_sorting_warnings')
    warnings_logger.setLevel(logging.INFO) # <-- CHANGED TO INFO

    # Prevent propagation to root logger if you don't want duplicate console logs
    # warnings_logger.propagate = False

    # Create a file handler for this logger
    file_handler = logging.FileHandler(warnings_log_file)
    file_handler.setLevel(logging.INFO) # <-- CHANGED TO INFO

    # Create a formatter and set it for the handler
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # Add the handler to the logger
    # Check if handlers are already added to prevent duplicates during reloads in debug mode
    if not warnings_logger.handlers:
        warnings_logger.addHandler(file_handler)

    app.logger.info(f"Dedicated blink sorting warnings logger configured. Warnings will be saved to {warnings_log_file}")
    # --- End of dedicated logger setup ---
    
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
    if not app_instance.debug:
        import logging
        logging.basicConfig(level=logging.INFO)

    app_instance.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)

