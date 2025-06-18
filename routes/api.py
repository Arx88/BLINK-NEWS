from flask import Flask, jsonify, request, Blueprint, current_app
from flask_cors import CORS
import os
import json
import glob # Added glob as requested
from datetime import datetime
import threading
import time
import hashlib
import logging # Added for dedicated logger
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

# Key function for sorting blinks, extracted for clarity and testability
def _sort_blinks_key(blink):
    votes = blink.get('votes', {})
    blink_id = blink.get('id', 'unknown_id') # Get blink ID for logging, default if not found
    warnings_logger = logging.getLogger('blink_sorting_warnings') # Get the dedicated logger

    raw_likes = votes.get('likes', 0)
    try:
        likes = int(raw_likes)
    except (ValueError, TypeError) as e:
        warnings_logger.warning(
            f"Blink {blink_id}: Failed to convert 'likes' value '{raw_likes}' to int. Defaulting to 0. Error: {e}"
        )
        likes = 0

    raw_dislikes = votes.get('dislikes', 0)
    try:
        dislikes = int(raw_dislikes)
    except (ValueError, TypeError) as e:
        warnings_logger.warning(
            f"Blink {blink_id}: Failed to convert 'dislikes' value '{raw_dislikes}' to int. Defaulting to 0. Error: {e}"
        )
        dislikes = 0

    total_votes = likes + dislikes
    interest_score = 0.0

    if total_votes > 0: # Calculate interest if there are any votes
        interest_score = float(likes) / total_votes
    # If total_votes is 0 (i.e., likes == 0 and dislikes == 0), interest_score remains 0.0

    raw_timestamp = blink.get('timestamp', 0)
    try:
        timestamp_val = float(raw_timestamp)
    except (ValueError, TypeError):
        timestamp_val = 0.0

    # The main sort call uses reverse=True
    if interest_score == 0.0:
        # For 0% interest (includes 0/0 votes and 0/N votes):
        # 1. Interest score is 0.0 (neutral for primary sort when all are 0.0).
        # 2. Dislikes (ascending, so key returns -dislikes due to reverse=True).
        # 3. Timestamp (ascending, so key returns -timestamp_val due to reverse=True).
        return (0.0, -dislikes, -timestamp_val)
    else:
        # For >0% interest blinks:
        # 1. Interest score (descending, so key returns interest_score).
        # 2. Likes (descending, so key returns likes).
        # 3. Timestamp (descending, so key returns timestamp_val).
        return (interest_score, likes, timestamp_val)

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
        app_instance = current_app._get_current_object()
        threading.Thread(target=collect_and_process_news, args=(app_instance,), daemon=True).start()
        
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

# --- New Blink Endpoints Start ---

@api_bp.route('/blinks/<blink_id>/vote', methods=['POST'])
def vote_on_blink(blink_id):
    """
    Records a vote (like or dislike) for a specific blink.
    Accepts blink_id from URL path and voteType from JSON body.
    """
    data = request.get_json()
    if not data or 'voteType' not in data:
        return jsonify({'error': 'Missing voteType in request body'}), 400

    vote_type = data.get('voteType')
    if vote_type not in ['like', 'dislike']:
        return jsonify({'error': 'Invalid voteType. Must be "like" or "dislike"'}), 400

    current_app.logger.info(f"Vote request received for blink_id: {blink_id}, voteType: {vote_type}")

    # Construct the file path for the blink
    blink_file_path = os.path.join(news_model.blinks_dir, f"{blink_id}.json")

    if not os.path.exists(blink_file_path):
        current_app.logger.error(f"Blink file not found for blink_id: {blink_id} at path: {blink_file_path}")
        return jsonify({'error': 'Blink not found'}), 404

    try:
        current_app.logger.info(f"Attempting to read/write file: {blink_file_path}")
        with open(blink_file_path, 'r+', encoding='utf-8') as f:
            blink_data = json.load(f)
            current_app.logger.info(f"Data loaded for {blink_id}: {blink_data}")

            # Initialize votes if not present
            if 'votes' not in blink_data:
                blink_data['votes'] = {'likes': 0, 'dislikes': 0}

            current_likes = blink_data['votes'].get('likes', 0)
            current_dislikes = blink_data['votes'].get('dislikes', 0)

            new_likes = current_likes
            new_dislikes = current_dislikes

            if vote_type == 'like':
                new_likes = current_likes + 1
                if current_dislikes > 0: # User is switching from dislike to like
                    new_dislikes = current_dislikes - 1
            elif vote_type == 'dislike':
                new_dislikes = current_dislikes + 1
                if current_likes > 0: # User is switching from like to dislike
                    new_likes = current_likes - 1

            blink_data['votes']['likes'] = max(0, new_likes)
            blink_data['votes']['dislikes'] = max(0, new_dislikes)

            # Write updated data back
            current_app.logger.info(f"Attempting to write data for {blink_id} to blink file: {blink_data}")
            f.seek(0)
            json.dump(blink_data, f, ensure_ascii=False, indent=2)
            f.truncate()
            current_app.logger.info(f"Successfully wrote data for {blink_id} to blink file.")

        # Also update the corresponding article file if it exists
        # This part mimics the behavior of news_model.update_vote
        article_file_path = os.path.join(news_model.articles_dir, f"{blink_id}.json")
        if os.path.exists(article_file_path):
            current_app.logger.info(f"Attempting to update votes in corresponding article file: {article_file_path} for blink_id: {blink_id}")
            try:
                with open(article_file_path, 'r+', encoding='utf-8') as f_article:
                    article_data = json.load(f_article)
                    article_data['votes'] = blink_data['votes'] # Sync votes
                    f_article.seek(0)
                    json.dump(article_data, f_article, ensure_ascii=False, indent=2)
                    f_article.truncate()
                    current_app.logger.info(f"Successfully updated votes in article file for blink_id: {blink_id}")
            except Exception as e:
                # Log this error, but the primary operation on blink was successful
                current_app.logger.error(f"Error updating votes in corresponding article {article_file_path} for blink_id {blink_id}: {e}")

        return jsonify({"message": "Vote recorded", "data": blink_data}), 200

    except json.JSONDecodeError as e:
        current_app.logger.error(f"Invalid JSON data in blink file for {blink_id}: {e}")
        return jsonify({'error': 'Invalid JSON data in blink file'}), 500
    except IOError as e:
        current_app.logger.error(f"IOError during vote operation for {blink_id}: {e}")
        return jsonify({'error': 'File operation failed'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error during vote operation for {blink_id}: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@api_bp.route('/blinks/<blink_id>', methods=['GET'])
def get_blink_by_id(blink_id):
    """
    Retrieves a specific blink by its ID.
    Reads from data/blinks/{blink_id}.json.
    """
    blink = news_model.get_blink(blink_id) # Leverages existing model method
    if not blink:
        return jsonify({'error': 'Blink not found'}), 404
    return jsonify(blink)

@api_bp.route('/blinks', methods=['GET'])
def get_all_blinks_sorted():
    """
    Retrieves all blinks, sorts them, and returns as JSON.
    Sort primary: votes.likes (desc), secondary: timestamp (desc).
    """
    blinks_path = news_model.blinks_dir
    all_blinks_data = []

    # Using glob to find all json files as per general instruction, though news_model.get_all_blinks() also works
    blink_files = glob.glob(os.path.join(blinks_path, "*.json"))

    # For logging purposes
    logged_count = 0
    max_logs = 3 # Log details for a few blinks

    for blink_file in blink_files:
        try:
            with open(blink_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                all_blinks_data.append(data)

                if logged_count < max_logs:
                    blink_id_for_log = data.get('id', 'unknown_id')
                    votes_for_log = data.get('votes', 'No votes field')
                    current_app.logger.info(f"[API /blinks] Loaded blink ID: {blink_id_for_log}, Votes: {votes_for_log}, File: {os.path.basename(blink_file)}")
                    logged_count += 1
        except json.JSONDecodeError:
            current_app.logger.error(f"Error decoding JSON from file {blink_file}")
            # Decide: skip this file or return an error for the whole request? For now, skip.
            continue
        except IOError as e:
            current_app.logger.error(f"IOError reading file {blink_file}: {e}")
            continue

    if not blink_files:
        current_app.logger.info("[API /blinks] No blink files found.")
    elif logged_count == 0 and blink_files: # If files exist but none were logged (e.g. all failed to load)
        current_app.logger.info(f"[API /blinks] Found {len(blink_files)} files, but failed to load/log details for any.")

    # Sort the blinks using the extracted key function
    all_blinks_data.sort(key=_sort_blinks_key, reverse=True)

    current_app.logger.info(f"[API /blinks] Returning {len(all_blinks_data)} blinks after processing and sorting.")
    return jsonify(all_blinks_data)

# --- New Blink Endpoints End ---

@api_bp.route('/article/<article_id>', methods=['GET'])
def get_article(article_id):
    """API para obtener un artículo específico"""
    article = news_model.get_article(article_id)
    
    if not article:
        return jsonify({'error': 'Artículo no encontrado'}), 404
    
    return jsonify(article)

@api_bp.route('/blink/<blink_id>', methods=['GET'])
def get_blink(blink_id): # This is the original /blink/<id> endpoint
    """API para obtener un blink específico"""
    blink = news_model.get_blink(blink_id)
    
    if not blink:
        return jsonify({'error': 'BLINK no encontrado'}), 404
    
    return jsonify(blink)

@api_bp.route('/vote', methods=['POST'])
def vote(): # This is the original /vote endpoint
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

def collect_and_process_news(app):
    """Recopila y procesa noticias de todas las fuentes"""
    with app.app_context():
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
                processed_in_this_run_ids = set() # Initialize set for this run

                for i, group in enumerate(newly_processed_groups): # Iterate over non-duplicate groups
                    # --- Start: In-run duplicate check based on group data (early check) ---
                    if not group: # Should have been caught earlier, but good to double check
                        continue

                    # Use first item of the group for tentative ID
                    first_item_in_group = group[0]
                    tentative_id_source_str = first_item_in_group.get('url', '') # Prioritize URL
                    if not tentative_id_source_str: # Fallback to title if URL is empty
                        tentative_id_source_str = first_item_in_group.get('title', '')

                    if not tentative_id_source_str: # If no URL and no title, cannot make reliable ID
                        print(f"SKIPPING group {i+1} due to missing URL and title for tentative ID generation.")
                        continue

                    tentative_group_id = hashlib.md5(tentative_id_source_str.encode()).hexdigest()

                    if tentative_group_id in processed_in_this_run_ids:
                        print(f"SKIPPING group {i+1} (tentative_id: {tentative_group_id}) as similar content was already processed in this run.")
                        continue
                    # --- End: In-run duplicate check based on group data ---

                    try: # This is the inner try for individual group processing
                        print(f"Procesando grupo {i+1}/{len(newly_processed_groups)} con {len(group)} noticias...")
                        blink = blink_generator.generate_blink_from_news_group(group) # AI calls are here

                        determined_category = blink.get('categories', ["general"])[0]

                        if determined_category not in allowed_publish_categories:
                            print(f"DEBUG_API_ROUTE: SKIPPING por CATEGORÍA: Blink '{blink.get('title', 'N/A')}' con categoría '{determined_category}' no está en allowed_publish_categories {allowed_publish_categories}.")
                            continue
                        else:
                            # This else block is for clarity; the actual saving logic follows.
                            # The print statement below will indicate it's proceeding.
                            pass # Explicitly doing nothing here, saving happens below if not skipped

                        # --- Start: In-run duplicate check based on generated blink ID (final check) ---
                        if blink['id'] in processed_in_this_run_ids:
                            print(f"SKIPPING blink '{blink.get('title', 'N/A')}' (ID: {blink['id']}) as its specific ID was already processed and saved in this run.")
                            continue
                        # --- End: In-run duplicate check based on generated blink ID ---

                        # If category was allowed, print that we are proceeding to save
                        if determined_category in allowed_publish_categories: # Re-check for safety or rely on not continuing
                             print(f"DEBUG_API_ROUTE: Blink '{blink.get('title', 'N/A')}' con categoría '{determined_category}' SÍ ESTÁ en allowed_categories. Procediendo a guardar.")

                        # Preserve existing votes if any
                        try:
                            existing_blink_data = news_model.get_blink(blink['id'])
                            if existing_blink_data and 'votes' in existing_blink_data:
                                blink['votes'] = existing_blink_data['votes']
                                # print(f"DEBUG: Preserving votes for blink {blink['id']}: {blink['votes']}") # Optional debug
                        except Exception as e:
                            # Log if there's an error fetching existing blink, but don't let it stop the process
                            print(f"DEBUG: Error trying to get existing blink for vote preservation (ID: {blink['id']}): {e}")
                            # Ensure votes key still exists if it was somehow removed or not set by generator
                            if 'votes' not in blink:
                                blink['votes'] = {'likes': 0, 'dislikes': 0}

                        print(f"DEBUG_API_ROUTE: Intentando guardar BLINK. ID: {blink['id']}, Título: {blink['title']}, Categorías: {blink.get('categories')}")
                        news_model.save_blink(blink['id'], blink)
                        print(f"DEBUG_API_ROUTE: BLINK GUARDADO EXITOSAMENTE. ID: {blink['id']}")
                        processed_in_this_run_ids.add(blink['id']) # Add ID after successful save of blink
                        # Also add the tentative_group_id to prevent re-processing of similar groups that might lead to different blink['id']s but were essentially the same source
                        processed_in_this_run_ids.add(tentative_group_id)


                        # ... (article creation and saving) ...
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
                        print(f"DEBUG_API_ROUTE: Error EXCEPCIÓN al procesar grupo de noticias {i+1} (Título tentativo: {group[0].get('title', 'N/A') if group else 'Grupo vacío'}): {e}")

                print(f"Recopilación completada. Se generaron {successful_blinks} BLINKs exitosamente.")
            else:
                print("No se encontraron noticias nuevas.")

        except Exception as e:
            if app and hasattr(app, 'logger'):
                app.logger.error(f"Error en la recopilación de noticias (hilo): {e}", exc_info=True)
            else:
                print(f"Error en la recopilación de noticias (hilo): {e}")

def schedule_news_collection(app):
    """Programa la recopilación periódica de noticias"""
    def collect_periodically(app_context):
        while True:
            try:
                # The app_context is already established by the caller of collect_periodically in the previous version.
                # However, to be consistent with collect_and_process_news now taking app, we pass it.
                # The with app_context.app_context() here becomes redundant if collect_and_process_news handles it.
                # For clarity and to ensure collect_and_process_news ALWAYS has context,
                # the primary context wrapping should be in collect_and_process_news.
                collect_and_process_news(app_context)
            except Exception as e:
                # Logging with app context here might be tricky if the error is context-related
                # Keeping simple print for the scheduler loop's own error reporting
                print(f"Error en el bucle de recopilación programada: {e}")
            
            # Esperar 2 horas antes de la próxima recopilación
            time.sleep(7200)
    
    # Iniciar en un hilo separado
    thread = threading.Thread(target=collect_periodically, args=(app,))
    thread.daemon = True
    thread.start()

# Función para inicializar las rutas de la API
def init_api(app):
    global scraper # Para modificar la instancia global del scraper
    global blink_generator # Para modificar la instancia global del blink_generator

    app_config = app.config.get('APP_CONFIG', {})
    scraper = NewsScraper(app_config) # Inicializar con la configuración de la app
    blink_generator = BlinkGenerator(app_config=app_config) # Re-inicializar con la configuración de la app

    app.register_blueprint(api_bp, url_prefix='/api')
    
    # Iniciar la recopilación periódica de noticias
    schedule_news_collection(app)
    
    return app
