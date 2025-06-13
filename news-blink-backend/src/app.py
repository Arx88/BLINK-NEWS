# Guardar como: news-blink-backend/src/app.py

from flask import Flask
from flask_cors import CORS

# Importar los blueprints directamente
from routes.api import api_bp
from routes.topic_search import topic_search_bp # La nueva ruta simplificada

def create_app():
    """Crea y configura la aplicación Flask de forma centralizada."""
    app = Flask(__name__)
    CORS(app, origins="*")
    
    # Registrar todas las rutas de la aplicación aquí
    app.register_blueprint(api_bp)
    app.register_blueprint(topic_search_bp, url_prefix='/api')
    
    print("--- Blueprints registrados ---")
    print("Rutas API generales en: /api")
    print("Ruta de búsqueda por tema en: /api/search-topic")
    print("----------------------------")

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)