import os
import sys # Keep sys for other diagnostics if needed

print("DEBUG: --- Attempting to disable .egg-info directory ---", flush=True)
egg_info_path = os.path.join(os.getcwd(), "news_blink_backend.egg-info") # Use getcwd() for safety
renamed_egg_info_path = os.path.join(os.getcwd(), "news_blink_backend.egg-info.disabled")
try:
    if os.path.exists(egg_info_path):
        os.rename(egg_info_path, renamed_egg_info_path)
        print(f"DEBUG: Renamed '{egg_info_path}' to '{renamed_egg_info_path}'. Exists now: {os.path.exists(renamed_egg_info_path)}", flush=True)
    else:
        print(f"DEBUG: Directory '{egg_info_path}' not found, no rename needed.", flush=True)
except Exception as e:
    print(f"DEBUG: Error renaming .egg-info directory: {e}", flush=True)
print("DEBUG: --- Finished .egg-info disable attempt ---", flush=True)

# Existing diagnostics should follow
# import os # os is already imported above
# import sys # sys is already imported above
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

print("DEBUG: --- Starting Step-wise Import Test ---", flush=True)
try:
    print("DEBUG: Attempting: import news_blink_backend", flush=True)
    import news_blink_backend
    print(f"DEBUG: Successfully imported news_blink_backend. Path: {news_blink_backend.__file__}", flush=True)

    print("DEBUG: Attempting: import news_blink_backend.src", flush=True)
    import news_blink_backend.src
    print(f"DEBUG: Successfully imported news_blink_backend.src. Path: {news_blink_backend.src.__file__}", flush=True)

    print("DEBUG: Attempting: import news_blink_backend.src.logger_config", flush=True)
    import news_blink_backend.src.logger_config
    print(f"DEBUG: Successfully imported news_blink_backend.src.logger_config. Path: {news_blink_backend.src.logger_config.__file__}", flush=True)

    print("DEBUG: Attempting final import: from news_blink_backend.src.logger_config import app_logger", flush=True)
    from news_blink_backend.src.logger_config import app_logger as configured_app_logger
    print(f"DEBUG: Successfully imported app_logger: {type(configured_app_logger)}", flush=True)

except Exception as e:
    print(f"DEBUG: !!! IMPORT TEST FAILED !!! Exception: {e}", flush=True)
    # Assign a basic fallback logger if import fails, to prevent NameError for configured_app_logger later
    # This allows the rest of the app to potentially start for further diagnostics, though it will log to console.
    print("DEBUG: Assigning fallback logger to configured_app_logger due to import failure.", flush=True)
    configured_app_logger = logging.getLogger('fallback_logger')
    configured_app_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    configured_app_logger.addHandler(console_handler)
    configured_app_logger.warning("Fallback logger is active due to import failure of primary app_logger.")

print("DEBUG: --- Finished Step-wise Import Test ---", flush=True)

# news_blink_backend.src.logger_config should be found if app.py is run from project root
# and news-blink-backend has __init__.py , and src has __init__.py
# from news_blink_backend.src.logger_config import app_logger as configured_app_logger # Moved into try-except block
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

    print("DEBUG: Attempting to flush handlers for configured_app_logger.", flush=True)
    for handler in configured_app_logger.handlers:
        try:
            handler.flush()
            print(f"DEBUG: Flushed handler: {handler}", flush=True)
        except Exception as e:
            print(f"DEBUG: Error flushing handler {handler}: {e}", flush=True)

    print("DEBUG: Sending direct test message via configured_app_logger.", flush=True)
    configured_app_logger.info("Direct test message from configured_app_logger to VoteFixLog.log.")

    print("DEBUG: Attempting to flush handlers for configured_app_logger AGAIN.", flush=True)
    for handler in configured_app_logger.handlers:
        try:
            handler.flush()
            print(f"DEBUG: Flushed handler AGAIN: {handler}", flush=True)
        except Exception as e:
            print(f"DEBUG: Error flushing handler {handler} AGAIN: {e}", flush=True)

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

