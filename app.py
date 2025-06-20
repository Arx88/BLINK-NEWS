import os
import sys # Keep sys for other diagnostics if needed

print("DEBUG: --- Attempting to disable .egg-info directory ---", flush=True)
# MODIFIED: news-blink-backend to news_blink_backend
egg_info_path = os.path.join(os.getcwd(), "news_blink_backend.egg-info") # Use getcwd() for safety
renamed_egg_info_path = os.path.join(os.getcwd(), "news_blink_backend.egg-info.disabled")
try:
    if os.path.exists(egg_info_path):
        os.rename(egg_info_path, renamed_egg_info_path)
        # MODIFIED: news-blink-backend to news_blink_backend (in f-string content)
        print(f"DEBUG: Renamed '{egg_info_path}' to '{renamed_egg_info_path}'. Exists now: {os.path.exists(renamed_egg_info_path)}", flush=True)
    else:
        # MODIFIED: news-blink-backend to news_blink_backend (in f-string content)
        print(f"DEBUG: Directory '{egg_info_path}' not found, no rename needed.", flush=True)
except Exception as e:
    print(f"DEBUG: Error renaming .egg-info directory: {e}", flush=True)
print("DEBUG: --- Finished .egg-info disable attempt ---", flush=True)

print(f"DEBUG: Current working directory: {os.getcwd()}", flush=True)
current_dir_to_list = os.getcwd()
print(f"DEBUG: Path whose contents will be listed: {current_dir_to_list}", flush=True)
print(f"DEBUG: sys.path at startup: {sys.path}", flush=True)
try:
    print(f"DEBUG: Listing contents of '{current_dir_to_list}': {os.listdir(current_dir_to_list)}", flush=True)
except Exception as e:
    print(f"DEBUG: Error listing contents of '{current_dir_to_list}': {e}", flush=True)

import json
import logging
import logging.handlers
from flask import Flask
from flask_cors import CORS

print("DEBUG: --- Starting Step-wise Import Test ---", flush=True)
try:
    # MODIFIED: news-blink-backend to news_blink_backend
    print("DEBUG: Attempting: import news_blink_backend", flush=True)
    import news_blink_backend
    print(f"DEBUG: Successfully imported news_blink_backend. Path: {news_blink_backend.__file__}", flush=True)

    # MODIFIED: news-blink-backend to news_blink_backend
    print("DEBUG: Attempting: import news_blink_backend.src", flush=True)
    import news_blink_backend.src
    print(f"DEBUG: Successfully imported news_blink_backend.src. Path: {news_blink_backend.src.__file__}", flush=True)

    # MODIFIED: news-blink-backend to news_blink_backend
    print("DEBUG: Attempting: import news_blink_backend.src.logger_config", flush=True)
    import news_blink_backend.src.logger_config
    print(f"DEBUG: Successfully imported news_blink_backend.src.logger_config. Path: {news_blink_backend.src.logger_config.__file__}", flush=True)

    # MODIFIED: news-blink-backend to news_blink_backend
    print("DEBUG: Attempting final import: from news_blink_backend.src.logger_config import app_logger", flush=True)
    from news_blink_backend.src.logger_config import app_logger as configured_app_logger
    print(f"DEBUG: Successfully imported app_logger: {type(configured_app_logger)}", flush=True)

except Exception as e:
    print(f"DEBUG: !!! IMPORT TEST FAILED !!! Exception: {e}", flush=True)
    print("DEBUG: Assigning fallback logger to configured_app_logger due to import failure.", flush=True)
    configured_app_logger = logging.getLogger('fallback_logger')
    configured_app_logger.setLevel(logging.DEBUG)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    configured_app_logger.addHandler(console_handler)
    configured_app_logger.warning("Fallback logger is active due to import failure of primary app_logger.")

print("DEBUG: --- Finished Step-wise Import Test ---", flush=True)

# --- BEGIN SYS.PATH MODIFICATION FOR routes.api ---
# This is added to help routes.api find models inside news_blink_backend.src
# Assumes this app.py is at the root of the project (/app).
# sys and os are already imported at the top of the file.
src_path = os.path.join(os.path.dirname(__file__), 'news_blink_backend', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path) # Insert at the beginning to give it priority
print(f"DEBUG: Modified sys.path in app.py to include: {src_path}", flush=True)
print(f"DEBUG: Full sys.path after modification: {sys.path}", flush=True)
# --- END SYS.PATH MODIFICATION ---

from routes.api import init_api
from routes.topic_search import topic_search_bp

CONFIG_FILE_PATH = 'config.json'

def load_app_config(app):
    config_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), CONFIG_FILE_PATH)
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
    app = Flask(__name__)
    CORS(app, origins="*")

    for handler in list(app.logger.handlers):
        app.logger.removeHandler(handler)
    for handler in configured_app_logger.handlers:
        app.logger.addHandler(handler)
    app.logger.setLevel(configured_app_logger.level)
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

    app_config = load_app_config(app)
    app.config['APP_CONFIG'] = app_config
    
    init_api(app)
    app.register_blueprint(topic_search_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app_instance = create_app()
    app_instance.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
