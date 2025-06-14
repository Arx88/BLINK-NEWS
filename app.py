
import json
import os
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

    app_instance.run(host='0.0.0.0', port=5000, debug=True)

