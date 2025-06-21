import os
import json
import math # Unused, can be removed
import logging
from flask import Blueprint, jsonify, request # Removed unused: current_app
from functools import cmp_to_key
from datetime import datetime
# Removed redundant: import logging
from ..logger_config import app_logger

api_bp = Blueprint('api_bp', __name__)

LOG_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'LOG')
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
VOTE_FIX_LOG_FILE = os.path.join(LOG_DIR_PATH, 'VoteFixLog.log')

vote_fix_logger = logging.getLogger('VoteFixLog')
vote_fix_logger.setLevel(logging.INFO)
vote_fix_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
# This specific handler for VoteFixLog can keep mode='w' if it's for isolated vote debugging sessions.
# The main app_logger is already mode='a'.
vote_fix_file_handler = logging.FileHandler(VOTE_FIX_LOG_FILE, mode='w')
vote_fix_file_handler.setFormatter(vote_fix_formatter)
if not vote_fix_logger.handlers:
    vote_fix_logger.addHandler(vote_fix_file_handler)
vote_fix_logger.propagate = False


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
BLINKS_DIR = os.path.join(DATA_DIR, 'blinks')
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')

# CONFIDENCE_FACTOR = 5 # This was unused

def get_blink_data(blink_id):
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_blink_data(blink_id, data):
    file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def calculate_interest(positive_votes, negative_votes):
    total_votes = positive_votes + negative_votes
    if total_votes == 0:
        return 50.0
    interest = (positive_votes / total_votes) * 100.0
    return interest

def compare_blinks(item1, item2):
    interest1 = item1.get('interest', 0.0)
    interest2 = item2.get('interest', 0.0)
    if interest1 != interest2:
        return -1 if interest1 > interest2 else 1

    likes1 = item1.get('positive_votes', 0)
    likes2 = item2.get('positive_votes', 0)
    if likes1 != likes2:
        return -1 if likes1 > likes2 else 1

    try:
        # Ensure publication_date is valid ISO format, default to a very old date if missing/invalid
        date1_str = item1.get('publication_date', '1970-01-01T00:00:00Z')
        date1 = datetime.fromisoformat(date1_str.replace('Z', '+00:00'))
    except ValueError:
        date1 = datetime.min.replace(tzinfo=datetime.timezone.utc)
    try:
        date2_str = item2.get('publication_date', '1970-01-01T00:00:00Z')
        date2 = datetime.fromisoformat(date2_str.replace('Z', '+00:00'))
    except ValueError:
        date2 = datetime.min.replace(tzinfo=datetime.timezone.utc)

    if date1 != date2:
        return -1 if date1 > date2 else 1
    return 0

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    app_logger.info(f"get_blinks called. Query parameters: {request.args}")
    try:
        all_blinks = []
        blink_files = [f for f in os.listdir(BLINKS_DIR) if f.endswith('.json')]
        app_logger.info(f"Found {len(blink_files)} JSON files in {BLINKS_DIR}")

        for filename in blink_files:
            blink_id = filename.split('.')[0]
            blink_data = get_blink_data(blink_id)
            if blink_data:
                blink_data.setdefault('id', blink_id)
                blink_data.setdefault('publication_date', datetime(1970, 1, 1, tzinfo=datetime.timezone.utc).isoformat())
                positive_votes = blink_data.setdefault('positive_votes', 0)
                negative_votes = blink_data.setdefault('negative_votes', 0)
                blink_data['interest'] = calculate_interest(positive_votes, negative_votes)
                all_blinks.append(blink_data)
            else:
                app_logger.warning(f"No data found for blink_id: {blink_id}")

        app_logger.info(f"Processed {len(all_blinks)} blinks for sorting.")
        sorted_blinks = sorted(all_blinks, key=cmp_to_key(compare_blinks))
        app_logger.info("Sorting complete.")

        app_logger.info("Applying isHot logic.")
        for i, blink_item in enumerate(sorted_blinks):
            if i < 4:
                blink_item['isHot'] = True
            else:
                blink_item['isHot'] = False
        app_logger.info("isHot logic application complete.")

        if sorted_blinks:
            sample_size = min(5, len(sorted_blinks))
            app_logger.info(f"--- DIAGNOSTIC LOG: First {sample_size} blinks PRE-JSONIFY ---")
            for i in range(sample_size):
                bi = sorted_blinks[i]
                log_output = {
                    "id": bi.get("id"), "title_snippet": bi.get("title", "")[:30],
                    "interest": bi.get("interest"), "isHot": bi.get("isHot", "MISSING_FIELD")
                }
                app_logger.info(f"Item {i+1}: {log_output}")
            app_logger.info(f"--- END DIAGNOSTIC LOG ---")

        app_logger.info(f"Returning {len(sorted_blinks)} blinks.")
        return jsonify(sorted_blinks)
    except Exception as e:
        app_logger.error(f"Error in get_blinks: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch blinks"}), 500

@api_bp.route('/blinks/<string:id>/vote', methods=['POST'])
def vote_blink(id):
    data = request.get_json()
    vote_type = data.get('voteType') # 'like' or 'dislike'
    # previousVote from frontend is 'positive'/'negative'/null. Convert to 'like'/'dislike'/null for internal logic.
    previous_vote_from_frontend = data.get('previousVote')
    user_id = data.get('userId')

    app_logger.info(f"vote_blink: ID={id}, User={user_id}, VoteType={vote_type}, PrevVoteFrontend={previous_vote_from_frontend}")

    if vote_type not in ['like', 'dislike']:
        app_logger.warning(f"Invalid vote_type: {vote_type}")
        return jsonify({"error": "Invalid vote type"}), 400

    blink_data = get_blink_data(id)
    if not blink_data:
        app_logger.warning(f"Blink not found: {id}")
        return jsonify({"error": "Blink not found"}), 404

    blink_data.setdefault('positive_votes', 0)
    blink_data.setdefault('negative_votes', 0)
    user_votes = blink_data.setdefault('user_votes', {})

    stored_user_vote = user_votes.get(user_id) # This is 'like', 'dislike', or None

    pv_before = blink_data['positive_votes']
    nv_before = blink_data['negative_votes']

    if vote_type == 'like':
        if stored_user_vote == 'like': # Clicking like again (un-liking)
            blink_data['positive_votes'] = max(0, pv_before - 1)
            user_votes.pop(user_id, None)
        elif stored_user_vote == 'dislike': # Changing dislike to like
            blink_data['negative_votes'] = max(0, nv_before - 1)
            blink_data['positive_votes'] = pv_before + 1
            user_votes[user_id] = 'like'
        else: # New like
            blink_data['positive_votes'] = pv_before + 1
            user_votes[user_id] = 'like'
    elif vote_type == 'dislike':
        if stored_user_vote == 'dislike': # Clicking dislike again (un-disliking)
            blink_data['negative_votes'] = max(0, nv_before - 1)
            user_votes.pop(user_id, None)
        elif stored_user_vote == 'like': # Changing like to dislike
            blink_data['positive_votes'] = max(0, pv_before - 1)
            blink_data['negative_votes'] = nv_before + 1
            user_votes[user_id] = 'dislike'
        else: # New dislike
            blink_data['negative_votes'] = nv_before + 1
            user_votes[user_id] = 'dislike'

    blink_data['currentUserVoteStatus'] = user_votes.get(user_id) # Update for the response
    blink_data['interest'] = calculate_interest(blink_data['positive_votes'], blink_data['negative_votes'])

    save_blink_data(id, blink_data)
    app_logger.info(f"Vote processed for {id}. New L/D: {blink_data['positive_votes']}/{blink_data['negative_votes']}. User '{user_id}' vote: {blink_data['currentUserVoteStatus']}")
    return jsonify({"data": blink_data})


@api_bp.route('/blinks/<string:id>', methods=['GET'])
def get_blink_details(id):
    app_logger.info(f"get_blink_details called for id: {id}")
    try:
        blink_data = get_blink_data(id)
        if not blink_data:
            return jsonify({"error": "Blink not found"}), 404

        blink_data.setdefault('positive_votes', 0)
        blink_data.setdefault('negative_votes', 0)
        blink_data['interest'] = calculate_interest(blink_data['positive_votes'], blink_data['negative_votes'])
        blink_data.setdefault('isHot', False)
        # Add user specific vote status for individual blink details
        user_id = request.args.get('userId')
        if user_id:
             blink_data['currentUserVoteStatus'] = blink_data.get('user_votes', {}).get(user_id)
        else:
            blink_data['currentUserVoteStatus'] = None


        article_file_path = os.path.join(ARTICLES_DIR, f"{id}.json")
        if os.path.exists(article_file_path):
            with open(article_file_path, 'r', encoding='utf-8') as f:
                article_content_data = json.load(f)
            detailed_blink = {**blink_data, "content": article_content_data.get("content", "")}
            return jsonify(detailed_blink)
        else:
            return jsonify(blink_data)

    except Exception as e:
        app_logger.error(f"Error fetching blink detail for {id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch blink details"}), 500
