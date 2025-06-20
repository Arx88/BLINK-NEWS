import os
import json
import math
import logging
from flask import Blueprint, jsonify, request, current_app
from functools import cmp_to_key
from datetime import datetime

# --- VERY EARLY DIAGNOSTICS ---
print("--- TOP OF api.py REACHED ---", flush=True)
# Raw file write test
raw_log_dir_test = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'LOG')
raw_log_path_test = os.path.join(raw_log_dir_test, 'VoteFixLog_RAW_TEST.log')
print(f"--- Attempting RAW write to: {raw_log_path_test} ---", flush=True)
try:
    if not os.path.exists(raw_log_dir_test):
        print(f"--- LOG directory for raw test not found, attempting to create: {raw_log_dir_test} ---", flush=True)
        os.makedirs(raw_log_dir_test, exist_ok=True)
        print(f"--- LOG directory for raw test creation attempted. ---", flush=True)

    with open(raw_log_path_test, "w") as f_test:
        f_test.write("RAW TEST WRITE FROM TOP OF api.py SUCCESSFUL AT " + datetime.now().isoformat() + "\n")
    print(f"--- RAW write to {raw_log_path_test} SUCCEEDED ---", flush=True)
except Exception as e_raw:
    print(f"--- RAW write to {raw_log_path_test} FAILED: {e_raw} ---", flush=True)
# --- END OF VERY EARLY DIAGNOSTICS ---

LOG_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'LOG')
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)

print(f"ROUTES.API: LOG_DIR_PATH for VoteFixLog.log is: {LOG_DIR_PATH}", flush=True)
VOTE_FIX_LOG_FILE = os.path.join(LOG_DIR_PATH, 'VoteFixLog.log')
print(f"ROUTES.API: Attempting to configure VoteFixLogLogger. Log file path: {VOTE_FIX_LOG_FILE}", flush=True)

vote_fix_logger = logging.getLogger('VoteFixLogLogger')
vote_fix_logger.setLevel(logging.DEBUG)
vote_fix_logger.propagate = False

for handler in vote_fix_logger.handlers[:]:
    vote_fix_logger.removeHandler(handler)
    handler.close()

file_handler_votefixlog = logging.FileHandler(VOTE_FIX_LOG_FILE, mode='w')
print(f"ROUTES.API: FileHandler configured for {VOTE_FIX_LOG_FILE} with mode 'w'.", flush=True)
formatter_votefixlog = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler_votefixlog.setFormatter(formatter_votefixlog)
vote_fix_logger.addHandler(file_handler_votefixlog)
print(f"ROUTES.API: FileHandler added to vote_fix_logger. Logger effective level: {vote_fix_logger.getEffectiveLevel()}", flush=True)

print("ROUTES.API: Attempting to write initial test message to vote_fix_logger.", flush=True)
vote_fix_logger.info("--- VoteFixLogLogger successfully initialized and configured in api.py ---")
print("ROUTES.API: Initial test message sent to vote_fix_logger.", flush=True)

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
    vote_fix_logger.info(f"get_blinks called. Query parameters: {request.args}")
    try:
        all_blinks = []
        vote_fix_logger.info(f"Scanning BLINKS_DIR: {BLINKS_DIR}")
        blink_files = [f for f in os.listdir(BLINKS_DIR) if f.endswith('.json')]
        vote_fix_logger.info(f"Found {len(blink_files)} raw .json files in {BLINKS_DIR}")

        for filename in blink_files:
            blink_id = filename.split('.')[0]
            vote_fix_logger.info(f"Processing blink_id: {blink_id}")
            blink_data = get_blink_data(blink_id)
            if blink_data:
                # Log raw blink_data (summary)
                blink_summary = {k: blink_data[k] for k in ('id', 'title', 'url', 'publication_date') if k in blink_data}
                vote_fix_logger.info(f"Raw blink_data for {blink_id} (summary): {blink_summary}")

                positive_votes = blink_data.setdefault('positive_votes', 0)
                negative_votes = blink_data.setdefault('negative_votes', 0)

                blink_data['interest'] = calculate_interest(positive_votes, negative_votes)
                vote_fix_logger.info(f"Calculated interest for {blink_id}: {blink_data['interest']}%")
                # Adding "Pre-append" log
                vote_fix_logger.info(f"Pre-append data for {blink_id}: PVotes={blink_data.get('positive_votes', 'NOT_SET')}, NVotes={blink_data.get('negative_votes', 'NOT_SET')}, Interest={blink_data.get('interest', 'NOT_SET')}, Keys={list(blink_data.keys())}")
                all_blinks.append(blink_data)
            else:
                vote_fix_logger.warning(f"No data found for blink_id: {blink_id} during get_blinks scan.")

        vote_fix_logger.info(f"Processed {len(all_blinks)} blinks for sorting.")
        if all_blinks:
            sample_pre_sort = all_blinks[0] if all_blinks else None
            if sample_pre_sort:
                vote_fix_logger.info(f"Sample blink data before sorting (first item): ID: {sample_pre_sort.get('id')}, Title: {sample_pre_sort.get('title_summary', 'N/A')}, Votes: +{sample_pre_sort.get('positive_votes',0)}/-{sample_pre_sort.get('negative_votes',0)}, Interest: {sample_pre_sort.get('interest',0.0)}%, Date: {sample_pre_sort.get('publication_date')}")

        vote_fix_logger.info(f"Calling sorted() with compare_blinks on {len(all_blinks)} blinks.")
        sorted_blinks = sorted(all_blinks, key=cmp_to_key(compare_blinks))
        vote_fix_logger.info("Sorting complete.")

        # Log sample of sorted blinks and total count
        if sorted_blinks:
            vote_fix_logger.info(f"Total blinks being returned after sorting: {len(sorted_blinks)}")
            sample_post_sort = sorted_blinks[0] if sorted_blinks else None
            if sample_post_sort:
                 vote_fix_logger.info(f"Sample blink data after sorting (first item): ID: {sample_post_sort.get('id')}, Title: {sample_post_sort.get('title_summary', 'N/A')}, Votes: +{sample_post_sort.get('positive_votes',0)}/-{sample_post_sort.get('negative_votes',0)}, Interest: {sample_post_sort.get('interest',0.0)}%, Date: {sample_post_sort.get('publication_date')}")
            # The existing diagnostic log block can serve as further detailed sample logging
            # START DIAGNOSTIC LOGGING BLOCK (using vote_fix_logger) - Retained for detailed sample
            sample_size = min(3, len(sorted_blinks))
            vote_fix_logger.info(f"--- DIAGNOSTIC LOG (Detail): Data for first {sample_size} of {len(sorted_blinks)} blinks PRE-JSONIFY ---")
            for i in range(sample_size):
                blink_to_log = sorted_blinks[i]
                log_output = {
                    "id": blink_to_log.get("id", "N/A"),
                    "title": blink_to_log.get("title", "N/A"), # Consider using title_summary if available
                    "positive_votes": blink_to_log.get("positive_votes", "N/A"),
                    "negative_votes": blink_to_log.get("negative_votes", "N/A"),
                    "interest": blink_to_log.get("interest", "N/A"),
                    "publication_date": blink_to_log.get("publication_date", "N/A")
                }
                vote_fix_logger.info(f"Blink {i+1} sample (detail): {log_output}")
            vote_fix_logger.info(f"--- END DIAGNOSTIC LOG (Detail) ---")
        else:
            vote_fix_logger.info("--- DIAGNOSTIC LOG (Detail): sorted_blinks list is empty PRE-JSONIFY ---")
        # END DIAGNOSTIC LOGGING BLOCK

        # --- ADDING NEW FINAL DATA SAMPLE LOGGING BLOCK ---
        if sorted_blinks:
            sample_size = min(3, len(sorted_blinks)) # Log up to 3 samples
            vote_fix_logger.info(f"--- FINAL DATA SAMPLE PRE-JSONIFY for /blinks (first {sample_size} of {len(sorted_blinks)}) ---")
            for i in range(sample_size):
                blink_to_log = sorted_blinks[i]
                log_output = {
                    "id": blink_to_log.get("id", "N/A"),
                    "title_snippet": blink_to_log.get("title", "N/A")[:30], # Snippet of title
                    "positive_votes": blink_to_log.get("positive_votes", "MISSING_OR_UNDEFINED"),
                    "negative_votes": blink_to_log.get("negative_votes", "MISSING_OR_UNDEFINED"),
                    "interest": blink_to_log.get("interest", "MISSING_OR_UNDEFINED"),
                    "publication_date": blink_to_log.get("publication_date", "N/A")
                }
                vote_fix_logger.info(f"Item {i+1}: {log_output}")
            vote_fix_logger.info(f"--- END FINAL DATA SAMPLE ---")
        else:
            vote_fix_logger.info("--- FINAL DATA PRE-JSONIFY for /blinks: sorted_blinks list is empty ---")
        # --- END OF NEW FINAL DATA SAMPLE LOGGING BLOCK ---

        vote_fix_logger.info(f"Returning {len(sorted_blinks)} blinks.")
        return jsonify(sorted_blinks)
    except Exception as e:
        vote_fix_logger.error(f"Error in get_blinks: {e}", exc_info=True)
        current_app.logger.error(f"Error fetching blinks: {e}") # Keep current_app.logger for now
        return jsonify({"error": "Failed to fetch blinks"}), 500

@api_bp.route('/blinks/<string:id>/vote', methods=['POST'])
def vote_blink(id):
    """Procesa un voto para un blink específico."""
    data = request.get_json()
    vote_fix_logger.info(f"vote_blink called for id: {id}. Payload: {data}")
    try:
        vote_type = data.get('voteType')
        previous_vote_status = data.get('previousVote')
        user_id = data.get('userId') # Logged in initial message

        if vote_type not in ['like', 'dislike']:
            vote_fix_logger.warning(f"Invalid vote_type: {vote_type} for blink {id}.")
            return jsonify({"error": "Invalid vote type"}), 400

        blink_data = get_blink_data(id)
        if not blink_data:
            vote_fix_logger.warning(f"Blink not found for id: {id} in vote_blink.")
            return jsonify({"error": "Blink not found"}), 404

        blink_summary = {k: blink_data[k] for k in ('id', 'title', 'positive_votes', 'negative_votes') if k in blink_data}
        vote_fix_logger.info(f"Fetched blink_data for {id} (summary): {blink_summary}")

        current_positive_votes = blink_data.setdefault('positive_votes', 0)
        current_negative_votes = blink_data.setdefault('negative_votes', 0)
        vote_fix_logger.info(f"Current votes for {id}: +{current_positive_votes}/-{current_negative_votes}")

        is_removing_vote = (vote_type == 'like' and previous_vote_status == 'like') or \
                          (vote_type == 'dislike' and previous_vote_status == 'dislike')

        action_taken = "No change"
        if vote_type == 'like':
            if is_removing_vote:
                action_taken = "Removing like"
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
                blink_data['currentUserVoteStatus'] = None
            elif previous_vote_status == 'dislike':
                action_taken = "Changing vote from dislike to like"
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
                blink_data['positive_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'like'
            else:
                action_taken = "Adding like"
                blink_data['positive_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'like'
        elif vote_type == 'dislike':
            if is_removing_vote:
                action_taken = "Removing dislike"
                blink_data['negative_votes'] = max(0, blink_data['negative_votes'] - 1)
                blink_data['currentUserVoteStatus'] = None
            elif previous_vote_status == 'like':
                action_taken = "Changing vote from like to dislike"
                blink_data['positive_votes'] = max(0, blink_data['positive_votes'] - 1)
                blink_data['negative_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'dislike'
            else:
                action_taken = "Adding dislike"
                blink_data['negative_votes'] += 1
                blink_data['currentUserVoteStatus'] = 'dislike'

        vote_fix_logger.info(f"Vote processing action for {id}: {action_taken}. User: {user_id}, Vote: {vote_type}, PrevStatus: {previous_vote_status}")
        vote_fix_logger.info(f"New votes for {id}: +{blink_data['positive_votes']}/-{blink_data['negative_votes']}")

        save_blink_data(id, blink_data)
        vote_fix_logger.info(f"Saved blink_data for {id}.")

        blink_data['interest'] = calculate_interest(blink_data['positive_votes'], blink_data['negative_votes'])
        vote_fix_logger.info(f"Recalculated interest for {id}: {blink_data['interest']}%")

        final_blink_summary = {k: blink_data[k] for k in ('id', 'title', 'positive_votes', 'negative_votes', 'interest', 'currentUserVoteStatus') if k in blink_data}
        vote_fix_logger.info(f"Returning updated blink data for {id} (summary): {final_blink_summary}")
        return jsonify({"data": blink_data})

    except Exception as e:
        vote_fix_logger.error(f"Error processing vote for blink {id}: {e}", exc_info=True)
        current_app.logger.error(f"Error processing vote for blink {id}: {e}") # Keep current_app.logger
        return jsonify({"error": "Failed to process vote"}), 500

@api_bp.route('/blinks/<string:id>', methods=['GET'])
def get_blink_details(id):
    """Obtiene los detalles de un blink específico y su artículo asociado."""
    vote_fix_logger.info(f"get_blink_details called for id: {id}")
    try:
        blink_data = get_blink_data(id)
        if not blink_data:
            vote_fix_logger.warning(f"Blink not found for id: {id} in get_blink_details.")
            return jsonify({"error": "Blink not found"}), 404

        blink_summary = {k: blink_data[k] for k in ('id', 'title', 'url', 'publication_date', 'positive_votes', 'negative_votes') if k in blink_data}
        vote_fix_logger.info(f"Fetched blink_data for {id} (summary): {blink_summary}")

        positive_votes = blink_data.setdefault('positive_votes', 0)
        negative_votes = blink_data.setdefault('negative_votes', 0)
        blink_data['interest'] = calculate_interest(positive_votes, negative_votes)
        vote_fix_logger.info(f"Calculated interest for {id}: {blink_data['interest']}%")

        article_file_path = os.path.join(ARTICLES_DIR, f"{id}.json")
        vote_fix_logger.info(f"Attempting to fetch article from: {article_file_path}")
        if not os.path.exists(article_file_path):
            vote_fix_logger.info(f"Article file not found for {id}. Returning blink data only.")
            return jsonify(blink_data)

        with open(article_file_path, 'r', encoding='utf-8') as f:
            article_content_data = json.load(f)

        article_content_summary = "Article content present" if article_content_data.get("content") else "Article content empty/missing"
        vote_fix_logger.info(f"Article content summary for {id}: {article_content_summary}")

        detailed_blink = {**blink_data, "content": article_content_data.get("content", "")}

        final_details_summary = {k: detailed_blink[k] for k in ('id', 'title', 'interest', 'publication_date') if k in detailed_blink}
        final_details_summary['content_present'] = bool(detailed_blink.get("content"))
        vote_fix_logger.info(f"Returning combined blink and article details for {id} (summary): {final_details_summary}")
        return jsonify(detailed_blink)
    except Exception as e:
        vote_fix_logger.error(f"Error fetching blink detail for {id}: {e}", exc_info=True)
        current_app.logger.error(f"Error fetching blink detail for {id}: {e}") # Keep current_app.logger
        return jsonify({"error": "Failed to fetch blink details"}), 500


