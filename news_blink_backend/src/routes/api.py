import os
import json
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
# Removed functools.cmp_to_key as local sorting is removed.
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
# BLINKS_DIR and ARTICLES_DIR are defined for clarity, though News model encapsulates path logic.
BLINKS_DIR = os.path.join(DATA_DIR, 'blinks')
ARTICLES_DIR = os.path.join(DATA_DIR, 'articles')

# Local helper functions like get_blink_data, save_blink_data,
# calculate_interest, compare_blinks are removed as their
# responsibilities are now handled by the News model or are not needed for get_blinks.

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    app_logger.info("get_blinks - API_PY_VERSION_1.2") # Version Marker Updated
    app_logger.info(f"get_blinks called, using News model. Query parameters: {request.args}")
    try:
        user_id = request.args.get('userId')
        news_instance = News(data_dir=DATA_DIR)

        all_processed_blinks = news_instance.get_all_blinks(user_id=user_id)
        app_logger.info(f"Retrieved {len(all_processed_blinks)} blinks directly from News model which should be pre-sorted and have 'interestPercentage'.")

        api_response_blinks = []
        for idx, blink_from_news_py in enumerate(all_processed_blinks):
            api_blink = blink_from_news_py.copy() # Work on a copy

            source_interest_percentage = blink_from_news_py.get('interestPercentage', 0.0)
            api_blink['interest'] = source_interest_percentage

            if 'interestPercentage' in api_blink: # Clean up by removing the old key
                api_blink.pop('interestPercentage')

            # Ensure other essential fields are present as expected by frontend
            api_blink.setdefault('id', blink_from_news_py.get('id', 'unknown_id')) # id should always be there from news.py
            api_blink.setdefault('title', blink_from_news_py.get('title', 'No Title'))

            # Ensure 'votes' dictionary and top-level positive/negative votes are present
            # News model's get_all_blinks is expected to provide 'votes' dict and positive/negative_votes
            current_votes_dict = api_blink.get('votes', {'likes': 0, 'dislikes': 0})
            api_blink['votes'] = current_votes_dict # Ensure the dict itself is there
            api_blink['positive_votes'] = api_blink.get('positive_votes', current_votes_dict.get('likes', 0))
            api_blink['negative_votes'] = api_blink.get('negative_votes', current_votes_dict.get('dislikes', 0))

            # 'publication_date' used by some old diagnostic logs if they were based on local sort.
            # 'publishedAt' is typically provided by news.py (from NewsItem).
            # Frontend (api.ts) transformBlinkToNewsItem uses 'publishedAt'.
            # Ensure both are present for robustness, 'publishedAt' being the primary from news.py.
            api_blink.setdefault('publishedAt', blink_from_news_py.get('publishedAt', datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()))
            api_blink.setdefault('publication_date', api_blink.get('publishedAt')) # Make publication_date mirror publishedAt


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
            blink_item['isHot'] = True if i < 4 else False
        app_logger.info("isHot logic application complete.")

        # --- DEFINITIVE isHot LOGGING (after assignment) ---
        app_logger.info("--- DEFINITIVE isHot LOGGING (after assignment) ---")
        log_sample_size = min(5, len(api_response_blinks))
        if log_sample_size > 0:
            for i in range(log_sample_size):
                item_to_log = api_response_blinks[i]
                app_logger.info(f"Item {i+1} PRE-JSONIFY: ID={item_to_log.get('id')}, Title='{item_to_log.get('title', '')[:30]}...', Interest={item_to_log.get('interest')}, isHot={item_to_log.get('isHot')}")
        else:
            app_logger.info("api_response_blinks is empty, cannot log isHot status sample.")
        app_logger.info("--- END DEFINITIVE isHot LOGGING ---")
        # --- END DEFINITIVE isHot LOGGING ---

        if api_response_blinks: # This is the existing diagnostic log block
            sample_size = min(5, len(api_response_blinks))
            app_logger.info(f"--- DIAGNOSTIC LOG: First {sample_size} blinks PRE-JSONIFY (from News model) ---")
            for i in range(sample_size):
                bi = api_response_blinks[i]
                log_output = {
                    "id": bi.get("id"), "title_snippet": bi.get("title", "")[:30],
                    "interest": bi.get("interest"),
                    "isHot": bi.get("isHot", False),
                    "positive_votes": bi.get("positive_votes"),
                    "negative_votes": bi.get("negative_votes"),
                    "currentUserVoteStatus": bi.get("currentUserVoteStatus"),
                    "publishedAt": bi.get("publishedAt")
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
    # Parameter name changed for clarity in News model, api.py sends it as 'previousVote'
    client_previous_vote_intention = data.get('previousVote')
    user_id = data.get('userId')

    app_logger.info(f"vote_blink route: ID={id}, User={user_id}, VoteType={vote_type}, ClientPrevVoteIntention={client_previous_vote_intention}")

    if not all([vote_type in ['like', 'dislike'], user_id]):
        app_logger.warning(f"Invalid vote_type or missing user_id.")
        return jsonify({"error": "Invalid vote type or user ID"}), 400

    try:
        news_instance = News(data_dir=DATA_DIR)
        updated_blink_data = news_instance.process_user_vote(
            blink_id=id,
            user_id=user_id,
            vote_type=vote_type,
            client_previous_vote_intention=client_previous_vote_intention # Pass client's idea for logging in model
        )

        if not updated_blink_data:
            app_logger.warning(f"Blink not found or vote processing failed for ID: {id}")
            return jsonify({"error": "Blink not found or vote failed"}), 404

        # Rename 'interestPercentage' to 'interest' for frontend from News model's response
        if 'interestPercentage' in updated_blink_data:
            updated_blink_data['interest'] = updated_blink_data.pop('interestPercentage')
        else:
            updated_blink_data['interest'] = 0.0 # Fallback if missing

        app_logger.info(f"Vote processed for {id} via News model. Returning updated_blink_data.")
        return jsonify({"data": updated_blink_data})

    except Exception as e:
        app_logger.error(f"Error in vote_blink for ID {id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to process vote"}), 500


@api_bp.route('/blinks/<string:id>', methods=['GET'])
def get_blink_details(id):
    user_id = request.args.get('userId')
    app_logger.info(f"get_blink_details called for id: {id}, user_id: {user_id}")
    try:
        news_instance = News(data_dir=DATA_DIR)
        blink_data = news_instance.get_blink(blink_id=id, user_id=user_id)

        if not blink_data:
            app_logger.warning(f"Blink detail not found for ID: {id} using News model.")
            return jsonify({"error": "Blink not found"}), 404

        # Rename 'interestPercentage' to 'interest' from News model's response
        if 'interestPercentage' in blink_data:
            blink_data['interest'] = blink_data.pop('interestPercentage')
        else:
            blink_data['interest'] = 0.0 # Fallback if missing

        blink_data.setdefault('isHot', False) # isHot is mainly for list view

        app_logger.info(f"Blink details retrieved for {id} using News model.")

        article_file_path = os.path.join(ARTICLES_DIR, f"{id}.json")
        if os.path.exists(article_file_path):
            with open(article_file_path, 'r', encoding='utf-8') as f:
                article_content_data = json.load(f)
            # Ensure the article content doesn't overwrite key fields from blink_data like interest, votes etc.
            # Create a new dictionary for the response.
            detailed_blink_response = {
                **blink_data,
                "content": article_content_data.get("content", "")
            }
            # Ensure no 'interestPercentage' is in the final response from article merge
            if 'interestPercentage' in detailed_blink_response:
                 detailed_blink_response.pop('interestPercentage')
            return jsonify(detailed_blink_response)
        else:
            app_logger.info(f"No separate article content file for {id}, returning blink data only.")
            return jsonify(blink_data)

    except Exception as e:
        app_logger.error(f"Error fetching blink detail for {id}: {e}", exc_info=True)
        return jsonify({"error": "Failed to fetch blink details"}), 500

# (Potentially add other imports if needed for this function, e.g., threading, time, but keep it minimal for now)

def collect_and_process_news():
    app_logger.info("collect_and_process_news - BACKGROUND TASK STARTED - API_PY_VERSION_1.2")
    news_model = None # Initialize to None for broader scope in error logging
    try:
        news_model = News(data_dir=DATA_DIR) # Use the global DATA_DIR

        # Call the get_all_blinks method. For a background task, user_id is likely None.
        # This method in news.py now handles all calculations and sorting.
        app_logger.info("collect_and_process_news: Calling news_model.get_all_blinks()")
        all_blinks = news_model.get_all_blinks()

        if all_blinks:
            app_logger.info(f"collect_and_process_news: Successfully fetched {len(all_blinks)} blinks.")
            # Placeholder for any further processing that this function was originally intended to do.
            # For now, just logging the count is sufficient to show it worked.
            # Example: Log details of the first few blinks fetched by the background task
            sample_size = min(3, len(all_blinks))
            app_logger.info(f"collect_and_process_news: Sample of fetched blinks (first {sample_size}):")
            for i in range(sample_size):
                blink = all_blinks[i]
                app_logger.info(
                    f"  - ID: {blink.get('id')}, Title: {blink.get('title', 'N/A')[:50]}, "
                    f"Interest: {blink.get('interestPercentage', 0.0):.2f}%"
                )
        else:
            app_logger.info("collect_and_process_news: news_model.get_all_blinks() returned no blinks or an empty list.")

    except AttributeError as ae:
        # This specific logging helps if the AttributeError somehow persists
        app_logger.error(f"collect_and_process_news - ATTRIBUTE ERROR: {ae}", exc_info=True)
        if news_model is not None:
            app_logger.error(f"collect_and_process_news: news_model type: {type(news_model)}")
            if hasattr(news_model, '__dict__'):
                 app_logger.error(f"collect_and_process_news: news_model attributes: {dir(news_model)}")
            else:
                 app_logger.error(f"collect_and_process_news: news_model has no __dict__ (dir: {dir(news_model)})")
        else:
            app_logger.error("collect_and_process_news: news_model was None when AttributeError occurred.")


    except Exception as e:
        app_logger.error(f"collect_and_process_news - BACKGROUND TASK ERROR: {e}", exc_info=True)
    finally:
        app_logger.info("collect_and_process_news - BACKGROUND TASK FINISHED - API_PY_VERSION_1.2")

# It's common for such background tasks to be initiated somewhere,
# but for this fix, just defining the function correctly is the goal.
# The actual initiation (e.g., in a thread in app.py) is outside this scope.
