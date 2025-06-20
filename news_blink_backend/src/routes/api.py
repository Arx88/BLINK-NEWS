import os
import json
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
# functools.cmp_to_key will be removed as local sorting is removed.
from ..logger_config import app_logger
from ..models.news import News # Import News model

api_bp = Blueprint('api_bp', __name__)

LOG_DIR_PATH = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'LOG')
if not os.path.exists(LOG_DIR_PATH):
    os.makedirs(LOG_DIR_PATH)
VOTE_FIX_LOG_FILE = os.path.join(LOG_DIR_PATH, 'VoteFixLog.log')

vote_fix_logger = logging.getLogger('VoteFixLog')
vote_fix_logger.setLevel(logging.INFO)
vote_fix_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
vote_fix_file_handler = logging.FileHandler(VOTE_FIX_LOG_FILE, mode='w')
vote_fix_file_handler.setFormatter(vote_fix_formatter)
if not vote_fix_logger.handlers:
    vote_fix_logger.addHandler(vote_fix_file_handler)
vote_fix_logger.propagate = False


DATA_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'data')
BLINKS_DIR = os.path.join(DATA_DIR, 'blinks') # Still needed for direct file access if any
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')


# Helper functions get_blink_data and save_blink_data might be deprecated
# if all data access goes through News model. For now, they might be used by
# other routes or internal logic if not fully refactored yet.
# However, the core logic in get_blinks, vote_blink, and get_blink_details
# will now primarily use the News instance.

# def get_blink_data(blink_id): # Potentially unused if News model handles all reads
#     file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
#     if not os.path.exists(file_path):
#         return None
#     with open(file_path, 'r', encoding='utf-8') as f:
#         return json.load(f)

# def save_blink_data(blink_id, data): # Potentially unused if News model handles all writes
#     file_path = os.path.join(BLINKS_DIR, f"{blink_id}.json")
#     with open(file_path, 'w', encoding='utf-8') as f:
#         json.dump(data, f, indent=4, ensure_ascii=False)

# The local helper functions (calculate_interest_simple, parse_datetime_for_sort, compare_blinks_simple)
# are removed as per the subtask to revert to News model usage for the main list.

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    app_logger.info(f"get_blinks called, using News model. Query parameters: {request.args}")
    try:
        user_id = request.args.get('userId')
        news_instance = News(data_dir=DATA_DIR)

        all_processed_blinks = news_instance.get_all_blinks(user_id=user_id)
        app_logger.info(f"Retrieved {len(all_processed_blinks)} blinks from News model.")

        api_response_blinks = []
        for idx, blink_from_news_py in enumerate(all_processed_blinks):
            api_blink = blink_from_news_py.copy() # Work on a copy

            source_interest_percentage = blink_from_news_py.get('interestPercentage', 0.0)
            api_blink['interest'] = source_interest_percentage

            if 'interestPercentage' in api_blink: # Clean up by removing the old key
                api_blink.pop('interestPercentage')

            # Ensure other essential fields are present as expected by frontend
            api_blink.setdefault('id', 'unknown_id') # id should always be there from news.py
            api_blink.setdefault('title', 'No Title')

            # Ensure 'votes' dictionary and top-level positive/negative votes are present
            current_votes_dict = api_blink.get('votes', {'likes': 0, 'dislikes': 0})
            api_blink['votes'] = current_votes_dict # Ensure the dict itself is there
            api_blink['positive_votes'] = api_blink.get('positive_votes', current_votes_dict.get('likes', 0))
            api_blink['negative_votes'] = api_blink.get('negative_votes', current_votes_dict.get('dislikes', 0))

            # 'publication_date' for sorting (used by isHot logic if it were sorted here, news.py sorts)
            # 'publishedAt' is often used in NewsItem type for display (e.g. by api.ts).
            # news.py's get_all_blinks should provide 'publishedAt'.
            # We ensure 'publication_date' exists, taking it from 'publishedAt' as primary source from news.py.
            api_blink.setdefault('publication_date', api_blink.get('publishedAt', datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()))
            # Ensure 'publishedAt' is also present if 'publication_date' was the only one (less likely from news.py)
            api_blink.setdefault('publishedAt', api_blink.get('publication_date', datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()))


            # Specific debug log for interest mapping (first 5 items)
            if idx < 5:
                app_logger.debug(
                    f"[API_DATA_MAPPING_DEBUG] Item ID: {api_blink.get('id')}, "
                    f"Source news.py 'interestPercentage': {source_interest_percentage}, "
                    f"Mapped api_blink['interest']: {api_blink.get('interest')}"
                )

            api_response_blinks.append(api_blink)

        app_logger.info(f"Transformed {len(api_response_blinks)} blinks for API response.")

        app_logger.info("Applying isHot logic to the top 4 items.")
        for i, blink_item in enumerate(api_response_blinks):
            if i < 4: # Top 4 based on news.py's sorting
                blink_item['isHot'] = True
            else:
                blink_item['isHot'] = False # Explicitly False for items not in top 4
        app_logger.info("isHot logic application complete.")

        if api_response_blinks:
            sample_size = min(5, len(api_response_blinks))
            app_logger.info(f"--- DIAGNOSTIC LOG: First {sample_size} blinks PRE-JSONIFY (from News model) ---")
            for i in range(sample_size):
                bi = api_response_blinks[i]
                log_output = {
                    "id": bi.get("id"), "title_snippet": bi.get("title", "")[:30],
                    "interest": bi.get("interest"),
                    "isHot": bi.get("isHot", False), # Default to False for logging
                    "positive_votes": bi.get("positive_votes"),
                    "negative_votes": bi.get("negative_votes"),
                    "currentUserVoteStatus": bi.get("currentUserVoteStatus"),
                    "publication_date": bi.get("publication_date"), # Log the date used by isHot if it were local
                    "publishedAt": bi.get("publishedAt") # Log the date from news.py
                }
                app_logger.info(f"Item {i+1}: {log_output}")
            app_logger.info(f"--- END DIAGNOSTIC LOG ---")

        app_logger.info(f"Returning {len(api_response_blinks)} blinks.")
        return jsonify(api_response_blinks)
    except Exception as e:
        app_logger.error(f"Error in get_blinks: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch blinks"}), 500

@api_bp.route('/blinks/<string:id>/vote', methods=['POST'])
def vote_blink(id):
    data = request.get_json()
    vote_type = data.get('voteType')  # 'like' or 'dislike'
    previous_vote_from_frontend = data.get('previousVote') # 'positive', 'negative', or null
    user_id = data.get('userId')

    app_logger.info(f"vote_blink: ID={id}, User={user_id}, VoteType={vote_type}, PrevVoteFrontend={previous_vote_from_frontend}")

    if not all([vote_type in ['like', 'dislike'], user_id]):
        app_logger.warning(f"Invalid vote_type or missing user_id.")
        return jsonify({"error": "Invalid vote type or user ID"}), 400

    try:
        news_instance = News(data_dir=DATA_DIR)
        # process_user_vote handles vote logic, updates file, and returns updated blink data
        updated_blink_data = news_instance.process_user_vote(
            blink_id=id,
            user_id=user_id,
            vote_type=vote_type, # 'like' or 'dislike'
            # process_user_vote expects previous_vote_on_frontend to be 'like', 'dislike', or None
            # The frontend sends 'positive'/'negative', so a mapping might be needed if not already handled
            # For now, assume process_user_vote can handle 'positive'/'negative' or it's mapped in News class
            previous_vote_on_frontend=previous_vote_from_frontend
        )

        if not updated_blink_data:
            app_logger.warning(f"Blink not found or vote processing failed for ID: {id}")
            return jsonify({"error": "Blink not found or vote failed"}), 404

        # Rename 'interestPercentage' to 'interest' for frontend
        updated_blink_data['interest'] = updated_blink_data.pop('interestPercentage', 0.0)

        app_logger.info(f"Vote processed for {id} via News model. New L/D: {updated_blink_data.get('positive_votes')}/{updated_blink_data.get('negative_votes')}. User '{user_id}' vote: {updated_blink_data.get('currentUserVoteStatus')}, New Interest: {updated_blink_data.get('interest')}")
        return jsonify({"data": updated_blink_data})

    except Exception as e:
        app_logger.error(f"Error in vote_blink for ID {id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to process vote"}), 500


@api_bp.route('/blinks/<string:id>', methods=['GET'])
def get_blink_details(id):
    app_logger.info(f"get_blink_details called for id: {id}. Query parameters: {request.args}")
    try:
        user_id = request.args.get('userId')
        news_instance = News(data_dir=DATA_DIR)

        blink_data = news_instance.get_blink(blink_id=id, user_id=user_id)

        if not blink_data:
            app_logger.warning(f"Blink detail not found for ID: {id} using News model.")
            return jsonify({"error": "Blink not found"}), 404

        # Rename 'interestPercentage' to 'interest'
        blink_data['interest'] = blink_data.pop('interestPercentage', 0.0)

        # 'isHot' is primarily for the main list. For details, it's usually false unless specifically set.
        blink_data.setdefault('isHot', False)
        # currentUserVoteStatus should already be set by get_blink if user_id was provided

        app_logger.info(f"Blink details retrieved for {id} using News model. Interest: {blink_data['interest']}, UserVote: {blink_data.get('currentUserVoteStatus')}")

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
