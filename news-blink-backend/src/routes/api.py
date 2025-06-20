import os
import json
import math
import logging
from flask import Blueprint, jsonify, request, current_app
from functools import cmp_to_key
from datetime import datetime

LOG_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'LOG')
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
VOTE_BAR_FIX_LOG_FILE = os.path.join(LOG_DIR_PATH, 'VoteBarFix.log')

vote_bar_fix_logger = logging.getLogger('VoteBarFixLogger')
vote_bar_fix_logger.setLevel(logging.DEBUG)
# Prevent duplicate logs if root logger is also configured for file output
vote_bar_fix_logger.propagate = False

# Remove any existing handlers to avoid duplication during reloads/multiple calls
for handler in vote_bar_fix_logger.handlers[:]:
    vote_bar_fix_logger.removeHandler(handler)
    handler.close()

file_handler_votebarfix = logging.FileHandler(VOTE_BAR_FIX_LOG_FILE, mode='w') # mode='w' to overwrite
formatter_votebarfix = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_votebarfix.setFormatter(formatter_votebarfix)
vote_bar_fix_logger.addHandler(file_handler_votebarfix)

api_bp = Blueprint('api_bp', __name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
BLINKS_DIR = os.path.join(DATA_DIR, 'blinks')
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')

# Factor de confianza para el cálculo del interés.
CONFIDENCE_FACTOR = 5

def get_blink_data(blink_id):
    """Lee los datos de un blink desde su archivo JSON."""
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_blink_data(blink_id, data):
    """Guarda los datos de un blink en su archivo JSON."""
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_interest(positive_votes, negative_votes):
    """Calcula el porcentaje de interés de un blink usando la fórmula revisada."""
    total_votes = positive_votes + negative_votes

    if total_votes == 0:
        return 50.0  # Noticia sin votos, 50% de interés

    # Fórmula: (Likes / (Likes + Dislikes)) * 100%
    interest = (positive_votes / total_votes) * 100.0
    return interest

def compare_blinks(item1, item2):
    """Función de comparación para ordenar los blinks según las reglas especificadas."""
    # Criterio Principal: Porcentaje de la Barra de Interés (de mayor a menor)
    # Asegurarse de que los valores de interés sean números
    interest1 = item1.get('interest', 0.0)
    interest2 = item2.get('interest', 0.0)

    if interest1 != interest2:
        return -1 if interest1 > interest2 else 1

    # Primer Desempate: Cantidad Absoluta de Likes (de mayor a menor)
    likes1 = item1.get('positive_votes', 0)
    likes2 = item2.get('positive_votes', 0)

    if likes1 != likes2:
        return -1 if likes1 > likes2 else 1

    # Segundo Desempate: Novedad (más reciente primero)
    # Asegurarse de que las fechas sean válidas para la comparación
    try:
        date1 = datetime.fromisoformat(item1.get('publication_date', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
    except ValueError:
        date1 = datetime.min # Fallback para fechas inválidas
    try:
        date2 = datetime.fromisoformat(item2.get('publication_date', '1970-01-01T00:00:00Z').replace('Z', '+00:00'))
    except ValueError:
        date2 = datetime.min # Fallback para fechas inválidas

    if date1 != date2:
        return -1 if date1 > date2 else 1

    return 0 # Si todo es igual, el orden no importa

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    """Obtiene todos los blinks, calcula su interés y los ordena."""
    try:
        all_blinks = []
        for filename in os.listdir(BLINKS_DIR):
            if filename.endswith('.json'):
                blink_id = filename.split('.')[0]
                blink_data = get_blink_data(blink_id)
                if blink_data:
                    # Asegurar que los contadores de votos existen
                    positive_votes = blink_data.setdefault('positive_votes', 0)
                    negative_votes = blink_data.setdefault('negative_votes', 0)
                    # Calcular y añadir el interés a cada blink
                    blink_data['interest'] = calculate_interest(positive_votes, negative_votes)
                    all_blinks.append(blink_data)

        # Ordenar la lista de blinks usando la función de comparación personalizada
        sorted_blinks = sorted(all_blinks, key=cmp_to_key(compare_blinks))

        # START DIAGNOSTIC LOGGING BLOCK (using vote_bar_fix_logger)
        if sorted_blinks:
            sample_size = min(3, len(sorted_blinks))
            vote_bar_fix_logger.info(f"--- DIAGNOSTIC LOG: Data for first {sample_size} of {len(sorted_blinks)} blinks PRE-JSONIFY ---")
            for i in range(sample_size):
                blink_to_log = sorted_blinks[i]
                log_output = {
                    "id": blink_to_log.get("id", "N/A"),
                    "title": blink_to_log.get("title", "N/A"),
                    "positive_votes": blink_to_log.get("positive_votes", "N/A"),
                    "negative_votes": blink_to_log.get("negative_votes", "N/A"),
                    "interest": blink_to_log.get("interest", "N/A"),
                    "publication_date": blink_to_log.get("publication_date", "N/A")
                }
                vote_bar_fix_logger.info(f"Blink {i+1} sample: {log_output}")
            vote_bar_fix_logger.info(f"--- END DIAGNOSTIC LOG ---")
        else:
            vote_bar_fix_logger.info("--- DIAGNOSTIC LOG: sorted_blinks list is empty PRE-JSONIFY ---")
        # END DIAGNOSTIC LOGGING BLOCK

        return jsonify(sorted_blinks)
    except Exception as e:
        current_app.logger.error(f"Error fetching blinks: {e}")
        return jsonify({"error": "Failed to fetch blinks"}), 500

@api_bp.route('/blinks/<string:id>/vote', methods=['POST'])
def vote_blink(id):
    """Procesa un voto para un blink específico."""
    try:
        data = request.get_json()
        vote_type = data.get('voteType') # Cambiado de 'vote_type' a 'voteType' para coincidir con el frontend
        previous_vote_status = data.get('previousVote') # Cambiado de 'previous_vote_status' a 'previousVote'
        user_id = data.get('userId') # Asegurarse de obtener el userId

        if vote_type not in ['like', 'dislike']:
            return jsonify({"error": "Invalid vote type"}), 400

        blink_data = get_blink_data(id)
        if not blink_data:
            return jsonify({"error": "Blink not found"}), 404

        # Asegurar que los contadores de votos existen y tienen valor por defecto
        blink_data.setdefault('positive_votes', 0)
        blink_data.setdefault('negative_votes', 0)

        # Determinar si se está quitando un voto (hacer clic en el mismo botón activo)
        is_removing_vote = (vote_type == 'like' and previous_vote_status == 'like') or \
                          (vote_type == 'dislike' and previous_vote_status == 'dislike')

        # Lógica para manejar el voto
        if vote_type == 'like':
            if is_removing_vote: # Quitar like
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
                blink_data['currentUserVoteStatus'] = None
            elif previous_vote_status == 'dislike': # Cambiar de dislike a like
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
                blink_data['positive_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'like'
            else: # Añadir like
                blink_data['positive_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'like'
        elif vote_type == 'dislike':
            if is_removing_vote: # Quitar dislike
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
                blink_data['currentUserVoteStatus'] = None
            elif previous_vote_status == 'like': # Cambiar de like a dislike
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
                blink_data['negative_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'dislike'
            else: # Añadir dislike
                blink_data['negative_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'dislike'

        save_blink_data(id, blink_data)
        # Recalcular el interés y devolver el blink actualizado
        blink_data['interest'] = calculate_interest(blink_data['positive_votes'], blink_data['negative_votes'])
        return jsonify({"data": blink_data}) # Envuelto en 'data' para coincidir con el frontend

    except Exception as e:
        current_app.logger.error(f"Error processing vote for blink {id}: {e}")
        return jsonify({"error": "Failed to process vote"}), 500

@api_bp.route('/blinks/<string:id>', methods=['GET'])
def get_blink_details(id):
    """Obtiene los detalles de un blink específico y su artículo asociado."""
    try:
        blink_data = get_blink_data(id)
        if not blink_data:
            return jsonify({"error": "Blink not found"}), 404

        # Calcular y añadir el interés al blink
        positive_votes = blink_data.setdefault('positive_votes', 0)
        negative_votes = blink_data.setdefault('negative_votes', 0)
        blink_data['interest'] = calculate_interest(positive_votes, negative_votes)

        article_file_path = os.path.join(ARTICLES_DIR, f"{id}.json")
        if not os.path.exists(article_file_path):
            # Si no hay artículo, devolver solo la info del blink con su interés
            return jsonify(blink_data)

        with open(article_file_path, 'r', encoding='utf-8') as f:
            article_content = json.load(f)

        # Combinar datos del blink y del artículo
        detailed_blink = {**blink_data, "content": article_content.get("content", "")} # Asumiendo que el contenido está bajo la clave 'content'

        return jsonify(detailed_blink)
    except Exception as e:
        current_app.logger.error(f"Error fetching blink detail for {id}: {e}")
        return jsonify({"error": "Failed to fetch blink details"}), 500


