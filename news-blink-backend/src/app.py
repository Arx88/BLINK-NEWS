from flask import Flask
from .routes.api import api_bp
from .routes.topic_search import topic_search_bp # Import the new blueprint
from .config import Config

def create_app():
    """
    Creates and configures the Flask application.
    """
    app = Flask(__name__)
    app.config.from_object(Config)

    # Register blueprints
    app.register_blueprint(api_bp, url_prefix='/api')
    app.register_blueprint(topic_search_bp, url_prefix='/search') # Register the topic search blueprint

    return app

if __name__ == '__main__':
    # This is for running the app with the Flask development server.
    # For production, use a WSGI server like Gunicorn.
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
