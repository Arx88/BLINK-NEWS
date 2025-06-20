import os
import json
import logging
from flask import Blueprint, jsonify, request
from datetime import datetime, timezone
from functools import cmp_to_key # Import cmp_to_key
from ..logger_config import app_logger
from ..models.news import News # Import News model - still used by other routes

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

# calculate_interest and compare_blinks are removed as News model handles this. - This comment is now outdated.

# --- Local Interest Calculation and Sorting Logic ---
def calculate_interest_simple(likes, dislikes):
    if likes + dislikes == 0:
        return 50.0
    return (likes / (likes + dislikes)) * 100.0

def parse_datetime_for_sort(iso_str):
    if not iso_str or iso_str == 'N/A': # Handle missing or N/A dates
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        # Attempt to parse, handling potential 'Z' for UTC
        if isinstance(iso_str, str):
            return datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
        elif isinstance(iso_str, datetime): # If it's already a datetime object
            if iso_str.tzinfo is None: # Ensure it's timezone-aware for comparison
                return iso_str.replace(tzinfo=timezone.utc)
            return iso_str
    except ValueError: # Fallback for unparseable strings
        app_logger.warning(f"Could not parse date string: {iso_str}, using min datetime.")
        return datetime.min.replace(tzinfo=timezone.utc)
    # Fallback if not string or datetime (should not happen with good data)
    app_logger.warning(f"Unexpected date type: {type(iso_str)}, using min datetime.")
    return datetime.min.replace(tzinfo=timezone.utc)


def compare_blinks_simple(item1, item2):
    # 1. Interest (desc)
    interest1 = item1.get('interest', 0.0)
    interest2 = item2.get('interest', 0.0)
    if interest1 != interest2:
        return -1 if interest1 > interest2 else 1

    # 2. Likes (desc) - Assuming 'positive_votes' holds the like count
    likes1 = item1.get('positive_votes', 0)
    likes2 = item2.get('positive_votes', 0)
    if likes1 != likes2:
        return -1 if likes1 > likes2 else 1

    # 3. Publication Date (desc)
    date1 = parse_datetime_for_sort(item1.get('publication_date'))
    date2 = parse_datetime_for_sort(item2.get('publication_date'))
    if date1 != date2:
        return -1 if date1 > date2 else 1
    return 0
# --- End Local Logic ---

@api_bp.route('/blinks', methods=['GET'])
def get_blinks():
    app_logger.info(f"get_blinks called with local file processing logic. Query parameters: {request.args}")
    # user_id = request.args.get('userId') # Not directly used in this version for list generation
                                          # but could be used if we need to set currentUserVoteStatus later.
    try:
        all_blinks_data = []
        blink_files = [f for f in os.listdir(BLINKS_DIR) if f.endswith('.json')]
        app_logger.info(f"Found {len(blink_files)} JSON files in {BLINKS_DIR} for local processing.")

        for filename in blink_files:
            blink_id = filename.split('.')[0]
            file_path = os.path.join(BLINKS_DIR, filename)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    blink_data_from_file = json.load(f)

                # Extract positive_votes and negative_votes
                # Common patterns: direct keys or nested under 'votes'
                positive_votes = blink_data_from_file.get('positive_votes', 0)
                negative_votes = blink_data_from_file.get('negative_votes', 0)
                if 'votes' in blink_data_from_file and isinstance(blink_data_from_file['votes'], dict):
                    positive_votes = blink_data_from_file['votes'].get('likes', positive_votes)
                    negative_votes = blink_data_from_file['votes'].get('dislikes', negative_votes)

                # Calculate interest using the local simple function
                interest = calculate_interest_simple(positive_votes, negative_votes)

                # Extract publication_date (handle potential variations like 'timestamp', 'publishedAt')
                pub_date_str = blink_data_from_file.get('publication_date',
                                   blink_data_from_file.get('timestamp',
                                       blink_data_from_file.get('publishedAt')))
                if not pub_date_str: # Default if no date field found
                    pub_date_str = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                # Create a dictionary for the current blink
                current_blink_api_item = {
                    'id': blink_id,
                    'title': blink_data_from_file.get('title', 'No Title'),
                    'summary': blink_data_from_file.get('summary', ''), # Frontend expects summary
                    'source': blink_data_from_file.get('source', 'Unknown Source'), # Frontend expects source
                    'image_url': blink_data_from_file.get('image_url', ''), # Frontend expects image_url
                    'positive_votes': positive_votes,
                    'negative_votes': negative_votes,
                    'votes': {'likes': positive_votes, 'dislikes': negative_votes}, # Frontend expects this structure too
                    'interest': interest,
                    'publication_date': pub_date_str,
                    # currentUserVoteStatus would require user_id and loading user_votes from file,
                    # or integration with News model logic if kept for that.
                    # For now, omitting it to keep this get_blinks self-contained for list generation.
                    'currentUserVoteStatus': None
                }
                all_blinks_data.append(current_blink_api_item)

            except FileNotFoundError:
                app_logger.warning(f"Blink file not found during iteration: {filename}")
            except json.JSONDecodeError:
                app_logger.warning(f"Error decoding JSON for blink file: {filename}")
            except Exception as e:
                app_logger.error(f"Error processing blink file {filename}: {e}", exc_info=True)

        app_logger.info(f"Processed {len(all_blinks_data)} blinks from files for sorting.")

        # Sort the blinks using the local comparison function
        sorted_blinks = sorted(all_blinks_data, key=cmp_to_key(compare_blinks_simple))
        app_logger.info("Local sorting complete.")

        app_logger.info("Applying isHot logic to the top 4 items.")
        for i, blink_item in enumerate(sorted_blinks):
            blink_item['isHot'] = i < 4
        app_logger.info("isHot logic application complete.")

        if sorted_blinks:
            sample_size = min(5, len(sorted_blinks))
            app_logger.info(f"--- DIAGNOSTIC LOG (LOCAL PROCESSING): First {sample_size} blinks PRE-JSONIFY ---")
            for i in range(sample_size):
                bi = sorted_blinks[i]
                log_output = {
                    "id": bi.get("id"), "title_snippet": bi.get("title", "")[:30],
                    "interest": bi.get("interest"),
                    "isHot": bi.get("isHot", False),
                    "positive_votes": bi.get("positive_votes"),
                    "negative_votes": bi.get("negative_votes"),
                    "publication_date_for_sort": parse_datetime_for_sort(bi.get('publication_date')).isoformat()
                }
                app_logger.info(f"Item {i+1}: {log_output}")
            app_logger.info(f"--- END DIAGNOSTIC LOG (LOCAL PROCESSING) ---")

        app_logger.info(f"Returning {len(sorted_blinks)} blinks (processed locally).")
        return jsonify(sorted_blinks)
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
