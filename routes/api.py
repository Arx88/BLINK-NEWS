from flask import Flask, jsonify, request, Blueprint, current_app
from flask_cors import CORS
import os
import json
from datetime import datetime
import threading
import time
# SequenceMatcher import removed as it's no longer directly used here

from models.scraper import NewsScraper
from models.blink_generator import BlinkGenerator
from models.news import News

# Crear blueprint para las rutas de la API
api_bp = Blueprint('api', __name__)

# Directorio para almacenar datos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Inicializar modelos
news_model = News(DATA_DIR)
# Scraper será inicializado en init_api para acceder a la configuración de la app
scraper = None
blink_generator = BlinkGenerator()

# Removed duplicated similarity function

@api_bp.route('/news', methods=['GET'])
def get_news():
    """API para obtener noticias en formato BLINK"""
    app_config = current_app.config.get('APP_CONFIG', {})
    max_articles_homepage = app_config.get('max_articles_homepage', 0)

    category = request.args.get('category', 'all')
    tab = request.args.get('tab', 'ultimas')
    
    # Obtener todos los blinks generados
    blinks = news_model.get_all_blinks()
    
    # Si no hay blinks o se solicita una actualización, recopilar nuevas noticias
    if not blinks or request.args.get('refresh') == 'true':
        # Iniciar recopilación en segundo plano
        threading.Thread(target=collect_and_process_news, daemon=True).start()
        
        # Si no hay blinks existentes, devolver mensaje de espera
        if not blinks:
            return jsonify({
                'status': 'processing',
                'message': 'Recopilando noticias, por favor intente nuevamente en unos segundos'
            })
    
    # Filtrar por categoría si es necesario
    if category != 'all':
        blinks = [blink for blink in blinks if category in blink.get('categories', [])]
    
    # Ordenar según la pestaña seleccionada
    if tab == 'tendencia':
        # Ordenar por popularidad (número de fuentes y votos)
        blinks.sort(key=lambda x: (len(x.get('sources', [])), 
                                  x.get('votes', {}).get('likes', 0) - 
                                  x.get('votes', {}).get('dislikes', 0)), 
                   reverse=True)
    elif tab == 'rumores':
        # Ordenar por menor número de fuentes (menos confirmación)
        blinks.sort(key=lambda x: len(x.get('sources', [])))
    else:  # 'ultimas' por defecto
        # Ordenar por timestamp (más reciente primero)
        blinks.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
    
    # Aplicar límite de artículos para la página principal
    if max_articles_homepage > 0 and len(blinks) > max_articles_homepage:
        blinks = blinks[:max_articles_homepage]

    return jsonify(blinks)

@api_bp.route('/article/<article_id>', methods=['GET'])
def get_article(article_id):
    """API para obtener un artículo específico"""
    article = news_model.get_article(article_id)
    
    if not article:
        return jsonify({'error': 'Artículo no encontrado'}), 404
    
    return jsonify(article)

@api_bp.route('/blink/<blink_id>', methods=['GET'])
def get_blink(blink_id):
    """API para obtener un blink específico"""
    blink = news_model.get_blink(blink_id)
    
    if not blink:
        return jsonify({'error': 'BLINK no encontrado'}), 404
    
    return jsonify(blink)

@api_bp.route('/vote', methods=['POST'])
def vote():
    """API para registrar votos"""
    data = request.json
    article_id = data.get('articleId')
    vote_type = data.get('type')  # 'like' o 'dislike'
    
    if not article_id or vote_type not in ['like', 'dislike']:
        return jsonify({'error': 'Datos inválidos'}), 400
    
    success = news_model.update_vote(article_id, vote_type)
    
    if not success:
        return jsonify({'error': 'Artículo no encontrado'}), 404
    
    return jsonify({'success': True, 'message': f'Voto {vote_type} registrado para el artículo {article_id}'})

@api_bp.route('/health', methods=['GET'])
def health_check():
    """API para verificar el estado del servicio"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '1.0.0'
    })

def collect_and_process_news():
    """Recopila y procesa noticias de todas las fuentes"""
    app_config = current_app.config.get('APP_CONFIG', {})
    allowed_publish_categories = app_config.get('allowed_publish_categories', ['tecnologia']) # Default to ['tecnologia'] if not set
    # Ensure it's a list, even if config had a single string by mistake (though json should handle list)
    if not isinstance(allowed_publish_categories, list):
        allowed_publish_categories = ['tecnologia']

    print(f"DEBUG: Allowed publish categories from config: {allowed_publish_categories}")
    try:
        print("Iniciando recopilación de noticias...")
        
        # Recopilar noticias de todas las fuentes
        news_items = scraper.scrape_all_sources()
        
        if news_items:
            print(f"Recopiladas {len(news_items)} noticias de todas las fuentes")
            
            # Guardar noticias crudas
            news_model.save_raw_news(news_items)
            
            # Agrupar noticias similares
            grouped_news = scraper.find_similar_news(news_items)
            
            # Obtener blinks existentes para la comprobación de duplicados
            existing_blinks = news_model.get_all_blinks()
            newly_processed_groups = []

            for group in grouped_news:
                if not group:  # Skip empty groups
                    continue

                representative_item = group[0] # Use the first item as representative
                is_duplicate = False
                for existing_blink in existing_blinks:
                    if 'title' in existing_blink and 'title' in representative_item:
                        # Use the new method from the scraper instance
                        sim_score = scraper.calculate_combined_similarity(representative_item['title'], existing_blink['title'])

                        if sim_score > scraper.similarity_threshold: # Accessing scraper instance's threshold
                            is_duplicate = True
                            print(f"Duplicate detected: New item '{representative_item['title']}' is too similar to existing blink '{existing_blink['title']}' (Score: {sim_score}). Skipping.")
                            break

                if not is_duplicate:
                    newly_processed_groups.append(group)

            # Generar BLINKs para cada grupo no duplicado
            successful_blinks = 0
            for i, group in enumerate(newly_processed_groups): # Iterate over non-duplicate groups
                try:
                    print(f"Procesando grupo {i+1}/{len(newly_processed_groups)} con {len(group)} noticias...")
                    blink = blink_generator.generate_blink_from_news_group(group)
                    
                    # Get the determined category for the blink (it's stored as a list)
                    determined_category = blink.get('categories', ["general"])[0] # Defaults to "general" if missing

                    # Check if the determined category is in the allowed list from config
                    if determined_category not in allowed_publish_categories:
                        print(f"SKIPPING: Blink '{blink.get('title', 'N/A')}' with category '{determined_category}' not in allowed_publish_categories {allowed_publish_categories}.")
                        continue # Skip this group/blink

                    # If category is allowed, proceed to save blink and article
                    news_model.save_blink(blink['id'], blink)
                    
                    article = {
                        'id': blink['id'],
                        'title': blink['title'],
                        'content': blink['content'],
                        'points': blink['points'],
                        'image': blink['image'],
                        'sources': blink['sources'],
                        'urls': blink['urls'],
                        'date': datetime.now().strftime('%d de %B %Y'),
                        'votes': blink.get('votes', {'likes': 0, 'dislikes': 0}),
                        'categories': blink.get('categories', ['general'])
                    }
                    news_model.save_article(blink['id'], article)
                    successful_blinks += 1
                    
                except Exception as e:
                    print(f"Error al procesar grupo de noticias {i+1}: {e}")
            
            print(f"Recopilación completada. Se generaron {successful_blinks} BLINKs exitosamente.")
        else:
            print("No se encontraron noticias nuevas.")
    
    except Exception as e:
        print(f"Error en la recopilación de noticias: {e}")

def schedule_news_collection():
    """Programa la recopilación periódica de noticias"""
    def collect_periodically():
        while True:
            try:
                collect_and_process_news()
            except Exception as e:
                print(f"Error en la recopilación programada: {e}")
            
            # Esperar 2 horas antes de la próxima recopilación
            time.sleep(7200)
    
    # Iniciar en un hilo separado
    thread = threading.Thread(target=collect_periodically)
    thread.daemon = True
    thread.start()

# Función para inicializar las rutas de la API
def init_api(app):
    global scraper # Para modificar la instancia global del scraper

    app_config = app.config.get('APP_CONFIG', {})
    scraper = NewsScraper(app_config) # Inicializar con la configuración de la app

    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Iniciar la recopilación periódica de noticias
    schedule_news_collection()
    
    return app
