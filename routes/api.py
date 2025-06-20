from flask import Flask, jsonify, request, Blueprint, current_app
from flask_cors import CORS
import os
import json
import glob # Added glob as requested
from datetime import datetime, timezone # Added timezone
from functools import cmp_to_key # Added cmp_to_key
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

def calculate_correct_interest(likes, dislikes):
    # Ensure likes and dislikes are integers
    try:
        likes = int(likes)
    except (ValueError, TypeError):
        likes = 0
    try:
        dislikes = int(dislikes)
    except (ValueError, TypeError):
        dislikes = 0

    total_votes = likes + dislikes
    if total_votes == 0:
        return 50.0  # 50% for no votes
    return (likes / total_votes) * 100.0

# Directorio para almacenar datos
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Inicializar modelos
news_model = News(DATA_DIR)
# Scraper será inicializado en init_api para acceder a la configuración de la app
scraper = None
blink_generator = BlinkGenerator()

# Removed duplicated similarity function

def compare_blinks_custom(item1, item2):
    logger = current_app.logger # Use Flask's app logger

    # Ensure 'calculated_interest_score' and votes are present, use defaults if not
    interest1 = item1.get('calculated_interest_score', 0.0)
    interest2 = item2.get('calculated_interest_score', 0.0)

    likes1 = item1.get('votes', {}).get('likes', 0)
    likes2 = item2.get('votes', {}).get('likes', 0)

    # Safely parse publication dates (assuming 'timestamp' field)
    # Default to a very old date if timestamp is missing or invalid
    date1_str = item1.get('timestamp', '1970-01-01T00:00:00Z')
    date2_str = item2.get('timestamp', '1970-01-01T00:00:00Z')

    try:
        date1 = datetime.fromisoformat(date1_str.replace('Z', '+00:00'))
        if date1.tzinfo is None or date1.tzinfo.utcoffset(date1) is None:
            date1 = date1.replace(tzinfo=timezone.utc)
    except ValueError:
        logger.warning(f"Invalid date format for item1 ID {item1.get('id')}: {date1_str}. Using fallback date.")
        date1 = datetime.min.replace(tzinfo=timezone.utc) # Ensure timezone aware for comparison
    try:
        date2 = datetime.fromisoformat(date2_str.replace('Z', '+00:00'))
        if date2.tzinfo is None or date2.tzinfo.utcoffset(date2) is None:
            date2 = date2.replace(tzinfo=timezone.utc)
    except ValueError:
        logger.warning(f"Invalid date format for item2 ID {item2.get('id')}: {date2_str}. Using fallback date.")
        date2 = datetime.min.replace(tzinfo=timezone.utc) # Ensure timezone aware

    # Log the items being compared (optional, can be very verbose)
    # logger.debug(f"Comparing ID {item1.get('id')} (I:{interest1:.2f}, L:{likes1}, D:{date1.isoformat()}) with ID {item2.get('id')} (I:{interest2:.2f}, L:{likes2}, D:{date2.isoformat()})")

    # 1. Primary: Interest Score (Descending)
    if interest1 != interest2:
        result = -1 if interest1 > interest2 else 1
        # logger.debug(f"  Interest diff: {item1.get('id') if result == -1 else item2.get('id')} wins ({interest1} vs {interest2})")
        return result

    # 2. Tie-breaker: Likes (Descending)
    if likes1 != likes2:
        result = -1 if likes1 > likes2 else 1
        # logger.debug(f"  Interest tied. Likes diff: {item1.get('id') if result == -1 else item2.get('id')} wins ({likes1} vs {likes2})")
        return result

    # 3. Tie-breaker: Publication Date (Most Recent First - Descending)
    if date1 != date2:
        result = -1 if date1 > date2 else 1
        # logger.debug(f"  Interest & Likes tied. Date diff: {item1.get('id') if result == -1 else item2.get('id')} wins ({date1.isoformat()} vs {date2.isoformat()})")
        return result

    # logger.debug("  Items are equal by all criteria.")
    return 0

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
    logger = current_app.logger
    data = request.get_json()

    logger.info(f"Enter vote_on_blink for ID '{blink_id}'. Payload: {data}")

    if not data or 'voteType' not in data:
        logger.warning(f"vote_on_blink for ID '{blink_id}': Missing 'voteType' in payload.")
        return jsonify({'error': 'Missing voteType in request body'}), 400

    vote_type = data.get('voteType')
    user_id = data.get('userId') # Assuming userId is passed in payload
    previous_vote_from_client = data.get('previousVote') # Informational

    if vote_type not in ['like', 'dislike']:
        logger.warning(f"vote_on_blink for ID '{blink_id}': Invalid 'voteType': {vote_type}")
        return jsonify({'error': 'Invalid voteType. Must be "like" or "dislike"'}), 400

    if not user_id:
        logger.warning(f"vote_on_blink for ID '{blink_id}': Missing 'userId' in payload.")
        return jsonify({'error': 'Missing userId in request body'}), 400


    # Construct the file path for the blink
    blink_file_path = os.path.join(news_model.blinks_dir, f"{blink_id}.json")

    if not os.path.exists(blink_file_path):
        logger.error(f"Blink file not found for blink_id: {blink_id} at path: {blink_file_path}")
        return jsonify({'error': 'Blink not found'}), 404

    try:
        logger.info(f"Attempting to read/write file: {blink_file_path}")
        with open(blink_file_path, 'r+', encoding='utf-8') as f:
            blink_data = json.load(f)

            # Initialize votes and user_votes if not present
            blink_data.setdefault('votes', {'likes': 0, 'dislikes': 0})
            blink_data.setdefault('user_votes', {})

            logger.debug(f"Blink {blink_id} state before vote: Votes={blink_data['votes']}, UserVotesMap={blink_data.get('user_votes')}")

            current_likes = blink_data['votes'].get('likes', 0)
            current_dislikes = blink_data['votes'].get('dislikes', 0)
            previous_vote_on_server = blink_data.get('user_votes', {}).get(user_id)
            logger.debug(f"User {user_id}'s previous vote on server for {blink_id}: {previous_vote_on_server}. Client said: {previous_vote_from_client}")

            action_taken = "No change determined (should not happen if previous_vote_on_server is handled)."
            # If user clicks 'like'
            if vote_type == 'like':
                if previous_vote_on_server == 'like': # Clicked like again (remove like)
                    blink_data['votes']['likes'] = max(0, current_likes - 1)
                    blink_data['user_votes'].pop(user_id, None)
                    action_taken = f"User '{user_id}' removed their 'like'."
                elif previous_vote_on_server == 'dislike': # Was disliked, now liked (change vote)
                    blink_data['votes']['likes'] = current_likes + 1
                    blink_data['votes']['dislikes'] = max(0, current_dislikes - 1)
                    blink_data['user_votes'][user_id] = 'like'
                    action_taken = f"User '{user_id}' changed vote from 'dislike' to 'like'."
                else: # No previous vote or previous was None (new like)
                    blink_data['votes']['likes'] = current_likes + 1
                    blink_data['user_votes'][user_id] = 'like'
                    action_taken = f"User '{user_id}' added new 'like'."
            # If user clicks 'dislike'
            elif vote_type == 'dislike':
                if previous_vote_on_server == 'dislike': # Clicked dislike again (remove dislike)
                    blink_data['votes']['dislikes'] = max(0, current_dislikes - 1)
                    blink_data['user_votes'].pop(user_id, None)
                    action_taken = f"User '{user_id}' removed their 'dislike'."
                elif previous_vote_on_server == 'like': # Was liked, now disliked (change vote)
                    blink_data['votes']['dislikes'] = current_dislikes + 1
                    blink_data['votes']['likes'] = max(0, current_likes - 1)
                    blink_data['user_votes'][user_id] = 'dislike'
                    action_taken = f"User '{user_id}' changed vote from 'like' to 'dislike'."
                else: # No previous vote or previous was None (new dislike)
                    blink_data['votes']['dislikes'] = current_dislikes + 1
                    blink_data['user_votes'][user_id] = 'dislike'
                    action_taken = f"User '{user_id}' added new 'dislike'."

            logger.info(f"Vote action for blink {blink_id} by user {user_id}: {action_taken}")
            logger.debug(f"Blink {blink_id} state after vote logic: Votes={blink_data['votes']}, UserVotesMap={blink_data.get('user_votes')}")

            # Write updated data back
            logger.info(f"[vote_on_blink] Attempting to write to file {blink_file_path}. Data being written for ID {blink_id}: {blink_data}")
            f.seek(0)
            json.dump(blink_data, f, ensure_ascii=False, indent=2)
            f.truncate()
            logger.info(f"[vote_on_blink] Successfully wrote and truncated file {blink_file_path} for ID {blink_id}.")

        # Also update the corresponding article file if it exists
        # This part mimics the behavior of news_model.update_vote
        article_file_path = os.path.join(news_model.articles_dir, f"{blink_id}.json")
        if os.path.exists(article_file_path):
            logger.info(f"Attempting to update votes in corresponding article file: {article_file_path} for blink_id: {blink_id}")
            try:
                with open(article_file_path, 'r+', encoding='utf-8') as f_article:
                    article_data = json.load(f_article)
                    # Sync votes and user_votes map to the article file
                    article_data['votes'] = blink_data['votes'].copy()
                    article_data['user_votes'] = blink_data.get('user_votes', {}).copy()
                    f_article.seek(0)
                    json.dump(article_data, f_article, ensure_ascii=False, indent=2)
                    f_article.truncate()
                    logger.info(f"Successfully updated votes in article file for blink_id: {blink_id}")
            except Exception as e:
                # Log this error, but the primary operation on blink was successful
                logger.error(f"Error updating votes in corresponding article {article_file_path} for blink_id {blink_id}: {e}", exc_info=True)

        blink_data['calculated_interest_score'] = calculate_correct_interest(blink_data['votes']['likes'], blink_data['votes']['dislikes'])
        blink_data['currentUserVoteStatus'] = blink_data.get('user_votes', {}).get(user_id) # 'like', 'dislike', or None
        logger.info(f"Returning updated blink data for {blink_id}: Interest={blink_data['calculated_interest_score']:.2f}%, UserVoteStatus={blink_data['currentUserVoteStatus']}")
        return jsonify({"message": "Vote recorded", "data": blink_data}), 200

    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON data in blink file for {blink_id}: {e}", exc_info=True)
        logger.error(f"[vote_on_blink] JSONDecodeError for ID {blink_id} in file {blink_file_path}: {e}")
        return jsonify({'error': 'Invalid JSON data in blink file'}), 500
    except IOError as e:
        current_app.logger.error(f"IOError during vote operation for {blink_id}: {e}")
        logger.error(f"[vote_on_blink] IOError for ID {blink_id} in file {blink_file_path}: {e}")
        return jsonify({'error': 'File operation failed'}), 500
    except Exception as e:
        current_app.logger.error(f"Unexpected error during vote operation for {blink_id}: {e}")
        logger.error(f"[vote_on_blink] Unexpected Exception for ID {blink_id} in file {blink_file_path}: {e}")
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
    logger = current_app.logger
    logger.info("Enter get_all_blinks_sorted: Fetching and sorting blinks.")
    blinks_path = news_model.blinks_dir
    all_blinks_data = []

    blink_files = glob.glob(os.path.join(blinks_path, "*.json"))

    for blink_file in blink_files:
        try:
            with open(blink_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

                current_likes = data.get('votes', {}).get('likes', 0)
                current_dislikes = data.get('votes', {}).get('dislikes', 0)
                data['calculated_interest_score'] = calculate_correct_interest(current_likes, current_dislikes)

                logger.debug(f"Pre-sort data for blink ID {data.get('id', 'N/A')}: Likes={current_likes}, Dislikes={current_dislikes}, PubDate={data.get('timestamp', 'N/A')}, Interest={data['calculated_interest_score']:.2f}%")
                all_blinks_data.append(data)
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file {blink_file}")
            continue
        except IOError as e:
            logger.error(f"IOError reading file {blink_file}: {e}")
            continue
        except Exception as e: # Catch any other potential errors during file processing
            logger.error(f"Unexpected error processing file {blink_file}: {e}", exc_info=True)
            continue

    logger.debug("--- Blinks before sorting (sample) ---")
    for i, blink_sample in enumerate(all_blinks_data[:5]):
        logger.debug(f"  {i+1}. ID: {blink_sample.get('id')}, Title: {blink_sample.get('title', 'N/A')[:30]}, Interest: {blink_sample.get('calculated_interest_score', 0.0):.2f}%, Likes: {blink_sample.get('votes',{}).get('likes',0)}, Timestamp: {blink_sample.get('timestamp')}")

    all_blinks_data.sort(key=cmp_to_key(compare_blinks_custom))

    logger.debug("--- Blinks after sorting (sample) ---")
    for i, blink_sample in enumerate(all_blinks_data[:5]):
        logger.debug(f"  {i+1}. ID: {blink_sample.get('id')}, Title: {blink_sample.get('title', 'N/A')[:30]}, Interest: {blink_sample.get('calculated_interest_score', 0.0):.2f}%, Likes: {blink_sample.get('votes',{}).get('likes',0)}, Timestamp: {blink_sample.get('timestamp')}")
    logger.info(f"Finished get_all_blinks_sorted. Returning {len(all_blinks_data)} blinks.")
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
