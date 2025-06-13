from flask import Flask
from flask_cors import CORS
from routes.api import init_api
from routes.topic_search import topic_search_bp

def create_app():
    """Crea y configura la aplicación Flask"""
    app = Flask(__name__)
    CORS(app, origins="*")  # Habilitar CORS para permitir solicitudes desde el frontend
    
    # Inicializar las rutas de la API
    init_api(app)
    
    # Registrar las nuevas rutas de búsqueda por tema
    app.register_blueprint(topic_search_bp, url_prefix='/api')
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)