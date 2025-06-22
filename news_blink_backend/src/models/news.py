import os
import sys
print("DEBUG_MODELS_NEWS: --- Path Diagnostics (models/news.py) ---", flush=True)
print(f"DEBUG_MODELS_NEWS: Current working directory (cwd): {os.getcwd()}", flush=True)
print(f"DEBUG_MODELS_NEWS: sys.path: {sys.path}", flush=True)
print(f"DEBUG_MODELS_NEWS: __file__: {__file__}", flush=True)
print(f"DEBUG_MODELS_NEWS: os.path.abspath(os.path.dirname(__file__)): {os.path.abspath(os.path.dirname(__file__))}", flush=True)
try:
    print(f"DEBUG_MODELS_NEWS: Listing contents of cwd '{os.getcwd()}': {os.listdir(os.getcwd())}", flush=True)
except Exception as e:
    print(f"DEBUG_MODELS_NEWS: Error listing contents of cwd '{os.getcwd()}': {e}", flush=True)
# Also list contents of /app if cwd is not /app, for comparison
if os.getcwd() != '/app':
    try:
        print(f"DEBUG_MODELS_NEWS: Listing contents of '/app': {os.listdir('/app')}", flush=True)
    except Exception as e:
        print(f"DEBUG_MODELS_NEWS: Error listing contents of '/app': {e}", flush=True)
print("DEBUG_MODELS_NEWS: --- End Path Diagnostics (models/news.py) ---", flush=True)

import json
from datetime import datetime, timezone
from functools import cmp_to_key

try:
    from news_blink_backend.src.logger_config import app_logger
    app_logger.info("Successfully imported 'app_logger' from 'news_blink_backend.src.logger_config' in models/news.py.")
except ImportError:
    import logging
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.DEBUG)
    if not app_logger.handlers:
        log_dir_relative_to_this_file = os.path.join(os.path.dirname(__file__), '..', 'LOG')
        log_directory = os.path.abspath(log_dir_relative_to_this_file)
        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
            except OSError as e:
                print(f"CRITICAL: Failed to create log directory {log_directory}. Error: {e}")
                ch = logging.StreamHandler()
                ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                app_logger.addHandler(ch)
                app_logger.error(f"Fallback logger: Directory creation failed for {log_directory}.")
        if os.path.exists(log_directory):
            log_file_path = os.path.join(log_directory, "VOTINGPROBLEMLOG.log")
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s')
            file_handler.setFormatter(formatter)
            app_logger.addHandler(file_handler)
            app_logger.info(f"Initialized fallback file logger for 'models.news' to: {log_file_path}")
        else:
            app_logger.warning("Directory for VOTINGPROBLEMLOG.log could not be created. Fallback logger is console only.")
    else:
        app_logger.info(f"Handlers already configured for logger '{app_logger.name}'. Skipping fallback setup.")
    app_logger.warning("Failed to import 'app_logger' from 'news_blink_backend.src.logger_config'. Using fallback logger for 'models.news'.")

import logging
vote_fix_logger_model_level = logging.getLogger('VoteFixLogLogger')

class News:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.raw_news_dir = os.path.join(data_dir, 'raw_news')
        self.blinks_dir = os.path.join(data_dir, 'blinks')
        self.articles_dir = os.path.join(data_dir, 'articles')
        app_logger.debug(f"News model initialized with data_dir: {data_dir}")
        os.makedirs(self.raw_news_dir, exist_ok=True)
        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)
        app_logger.debug(f"Required directories ensured: raw_news, blinks, articles.")

    def save_raw_news(self, news_items):
        filename = f"raw_news_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.raw_news_dir, filename)
        app_logger.debug(f"Attempting to save {len(news_items)} raw news items to {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved {len(news_items)} raw news items to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving raw news to {filepath}: {e}", exc_info=True)

    def save_blink(self, blink_id, blink_data):
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        log_data_subset = {
            'id': blink_data.get('id'),
            'title': blink_data.get('title_for_logging', blink_data.get('title', 'N/A')[:50]),
            'votes': blink_data.get('votes'),
            'user_votes': blink_data.get('user_votes')
        }
        if blink_data.get('user_votes'):
            vote_fix_logger_model_level.info(f"Saving blink_id='{blink_id}' (potentially after vote). Votes: {log_data_subset.get('votes')}, UserVotes sample: {list(log_data_subset.get('user_votes', {}).items())[:2]}")
        app_logger.debug(f"Attempting to save blink_id='{blink_id}' to {filepath}. Data subset: {json.dumps(log_data_subset)}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blink_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved blink_id='{blink_id}' to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving blink_id='{blink_id}' to {filepath}: {e}", exc_info=True)
            raise

    def get_blink(self, blink_id, user_id=None):
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.debug(f"Attempting to get blink_id='{blink_id}' from {filepath} for user_id='{user_id}'")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                data.setdefault('votes', {}).setdefault('likes', 0)
                data['votes'].setdefault('dislikes', 0)
                data.setdefault('user_votes', {})
                if user_id:
                    data['currentUserVoteStatus'] = self._get_user_vote_status(data, user_id)
                    vote_fix_logger_model_level.info(f"get_blink for voting/display: id='{blink_id}', user_id='{user_id}'. Votes: {data.get('votes')}, UserVotes: {data.get('user_votes', {}).get(user_id, 'N/A')}, Determined status: {data['currentUserVoteStatus']}")
                else:
                    data['currentUserVoteStatus'] = None
                    vote_fix_logger_model_level.debug(f"get_blink for general purpose: id='{blink_id}', no user_id. Votes: {data.get('votes')}")
                data['interestPercentage'] = self.calculate_interest_percentage(data)
                app_logger.debug(f"Successfully loaded blink_id='{blink_id}'. Votes: {data.get('votes')}, UserVote: {data.get('currentUserVoteStatus')}, Interest: {data.get('interestPercentage')}")
                return data
            except Exception as e:
                app_logger.error(f"Error reading or processing blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
                vote_fix_logger_model_level.error(f"Error reading or processing blink_id='{blink_id}' in get_blink: {e}", exc_info=True)
        else:
            app_logger.warning(f"Blink file not found for blink_id='{blink_id}' at {filepath}")
        return None

    def save_article(self, article_id, article_data):
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        app_logger.debug(f"Attempting to save article_id='{article_id}' to {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved article_id='{article_id}' to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving article_id='{article_id}' to {filepath}: {e}", exc_info=True)
            raise

    def get_article(self, article_id):
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        app_logger.debug(f"Attempting to get article_id='{article_id}' from {filepath}")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                votes = data.setdefault('votes', {})
                votes.setdefault('likes', 0)
                votes.setdefault('dislikes', 0)
                data.setdefault('user_votes', {})
                app_logger.debug(f"Successfully loaded article_id='{article_id}'")
                return data
            except Exception as e:
                app_logger.error(f"Error reading article_id='{article_id}' from {filepath}: {e}", exc_info=True)
        else:
            app_logger.warning(f"Article file not found for article_id='{article_id}' at {filepath}")
        return None

    def process_user_vote(self, blink_id, user_id, vote_type, client_previous_vote_intention):
        # client_previous_vote_intention is logged but not used for core logic.
        # Server-side state (server_known_user_vote) is authoritative.

        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.info(
            f"process_user_vote ENTER: blink_id='{blink_id}', user_id='{user_id}', "
            f"client_vote_type='{vote_type}', client_prev_vote_intention='{client_previous_vote_intention}'"
        )

        if not os.path.exists(filepath):
            app_logger.warning(f"process_user_vote: Blink file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
        except Exception as e:
            app_logger.error(f"process_user_vote: Error reading/decoding {filepath}: {e}", exc_info=True)
            return None

        # Initialize votes and user_votes map if they don't exist
        if 'votes' not in article_data:
            article_data['votes'] = {}
        if 'likes' not in article_data['votes']:
            article_data['votes']['likes'] = 0
        if 'dislikes' not in article_data['votes']:
            article_data['votes']['dislikes'] = 0
        if 'user_votes' not in article_data:
            article_data['user_votes'] = {}

        likes = article_data['votes']['likes']
        dislikes = article_data['votes']['dislikes']
        user_votes_map = article_data['user_votes']

        server_known_user_vote = user_votes_map.get(user_id)

        app_logger.debug(
            f"process_user_vote PRE-LOGIC: blink_id='{blink_id}', user_id='{user_id}', "
            f"Initial Counts L/D: {likes}/{dislikes}, "
            f"ServerKnownUserVote: '{server_known_user_vote}', ClientVoteType: '{vote_type}'"
        )
        action_taken_log = "No change in vote state."

        # New logic based on user feedback
        if server_known_user_vote == vote_type:  # Clicking an active button - remove vote
            if vote_type == 'like':
                likes = max(0, likes - 1)
                action_taken_log = f"User '{user_id}' UNLIKED (removed existing like)."
            elif vote_type == 'dislike':
                dislikes = max(0, dislikes - 1)
                action_taken_log = f"User '{user_id}' UNDISLIKED (removed existing dislike)."
            user_votes_map.pop(user_id, None)

        else:  # New vote or switching vote
            # First, revert previous vote if any
            if server_known_user_vote == 'like':
                likes = max(0, likes - 1)
            elif server_known_user_vote == 'dislike':
                dislikes = max(0, dislikes - 1)

            # Now apply the new vote
            if vote_type == 'like':
                likes += 1
                # More specific logging for new vs switched
                if server_known_user_vote == 'dislike':
                     action_taken_log = f"User '{user_id}' SWITCHED vote from DISLIKE to LIKE."
                elif server_known_user_vote is None:
                     action_taken_log = f"User '{user_id}' NEWLY LIKED."
                else: # Should not happen if logic is server_known_user_vote != vote_type and not None
                     action_taken_log = f"User '{user_id}' voted LIKE (unexpected previous state: {server_known_user_vote})."


            elif vote_type == 'dislike':
                dislikes += 1
                # More specific logging for new vs switched
                if server_known_user_vote == 'like':
                     action_taken_log = f"User '{user_id}' SWITCHED vote from LIKE to DISLIKE."
                elif server_known_user_vote is None:
                     action_taken_log = f"User '{user_id}' NEWLY DISLIKED."
                else: # Should not happen
                     action_taken_log = f"User '{user_id}' voted DISLIKE (unexpected previous state: {server_known_user_vote})."
            user_votes_map[user_id] = vote_type

        article_data['votes']['likes'] = likes
        article_data['votes']['dislikes'] = dislikes
        article_data['user_votes'] = user_votes_map

        # Recalculate interestPercentage using the (now simple) formula
        article_data['interestPercentage'] = self.calculate_interest_percentage(article_data)
        article_data['currentUserVoteStatus'] = user_votes_map.get(user_id)

        app_logger.info(
            f"process_user_vote POST-LOGIC: blink_id='{blink_id}', user_id='{user_id}'. "
            f"Action: {action_taken_log}. "
            f"Final Counts L/D: {likes}/{dislikes}. "
            f"User vote in map: {article_data['currentUserVoteStatus']}. "
            f"InterestPercentage: {article_data['interestPercentage']:.2f}%"
        )
        vote_fix_logger.info( # Using vote_fix_logger as well for dedicated vote logging
            f"Vote for {blink_id}, user {user_id}: {action_taken_log}. L/D: {likes}/{dislikes}. "
            f"User map: {article_data['currentUserVoteStatus']}. Interest: {article_data['interestPercentage']:.2f}%"
        )

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"process_user_vote: Successfully saved updated blink_id='{blink_id}' to {filepath}")

            full_article_path = os.path.join(self.articles_dir, f"{blink_id}.json")
            if os.path.exists(full_article_path):
                try:
                    with open(full_article_path, 'r', encoding='utf-8') as f_article:
                        full_article_content = json.load(f_article)
                    full_article_content['votes'] = article_data['votes'].copy()
                    full_article_content['user_votes'] = article_data['user_votes'].copy()
                    # Also update interest in the article file for consistency if it exists there
                    if 'interestPercentage' in full_article_content or 'interest' in full_article_content :
                         full_article_content['interestPercentage'] = article_data['interestPercentage']
                         if 'interest' in full_article_content : full_article_content.pop('interest',None)
                    with open(full_article_path, 'w', encoding='utf-8') as f_article_w:
                        json.dump(full_article_content, f_article_w, ensure_ascii=False, indent=2)
                    app_logger.debug(f"process_user_vote: Synced votes/interest to full article file: {full_article_path}")
                except Exception as e_article:
                    app_logger.warning(f"process_user_vote: Non-critical error syncing to full article {full_article_path}: {e_article}", exc_info=True)

        except IOError as e:
            app_logger.error(f"process_user_vote: IOError saving blink_id='{blink_id}' to {filepath}: {e}", exc_info=True)
            return None

        return article_data

    def _get_user_vote_status(self, blink_data, user_id):
        if not isinstance(blink_data, dict):
            app_logger.warning(f"_get_user_vote_status: blink_data is not a dictionary for user_id='{user_id}'.")
            return None
        status = blink_data.get('user_votes', {}).get(user_id)
        app_logger.debug(f"_get_user_vote_status: For user_id='{user_id}', vote_status='{status}'.")
        return status

    def calculate_interest_percentage(self, blink_data): # Removed confidence_factor_c
        vote_fix_logger = logging.getLogger('VoteFixLogLogger')
        blink_id_for_log = blink_data.get('id', 'N/A') if isinstance(blink_data, dict) else 'N/A'

        if not isinstance(blink_data, dict) or 'votes' not in blink_data:
            app_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes'. ID: {blink_id_for_log}. Returning 0.0 interest.")
            vote_fix_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes' for ID='{blink_id_for_log}'. Returning 0.0 (Simple Logic).")
            return 0.0

        current_votes = blink_data['votes']
        likes = current_votes.get('likes', 0)
        dislikes = current_votes.get('dislikes', 0)
        total_votes = likes + dislikes

        if total_votes == 0:
            interest = 50.0
        else:
            interest = (likes / total_votes) * 100.0

        app_logger.debug(
            f"calculate_interest_percentage for ID {blink_id_for_log}: "
            f"L={likes}, D={dislikes}, Total={total_votes} -> Interest={interest:.2f}% (Simple Logic)"
        )
        vote_fix_logger.info(
            f"calculate_interest_percentage result for ID='{blink_id_for_log}': "
            f"Calculated Interest={interest:.2f}% (Simple Logic)"
        )
        return interest

    def _compare_blinks(self, blink_a, blink_b):
        def parse_datetime_for_compare(published_at_str):
            if not published_at_str:
                return datetime.min.replace(tzinfo=timezone.utc)
            try:
                dt = datetime.fromisoformat(str(published_at_str).replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                app_logger.warning(f"Could not parse datetime string '{published_at_str}' in _compare_blinks. Using fallback minimum date.", exc_info=False)
                return datetime.min.replace(tzinfo=timezone.utc)

        interest_a = blink_a.get('interestPercentage', 0.0)
        interest_b = blink_b.get('interestPercentage', 0.0)
        if interest_a != interest_b:
            return -1 if interest_a > interest_b else 1

        likes_a = blink_a.get('votes', {}).get('likes', 0)
        likes_b = blink_b.get('votes', {}).get('likes', 0)
        if likes_a != likes_b:
            return -1 if likes_a > likes_b else 1

        date_a = parse_datetime_for_compare(blink_a.get('publishedAt'))
        date_b = parse_datetime_for_compare(blink_b.get('publishedAt'))
        if date_a != date_b:
            return -1 if date_a > date_b else 1

        return 0

    def get_all_blinks(self, user_id=None):
        app_logger.info(f"get_all_blinks called. user_id='{user_id}' (using Simple Logic for interest/sort)")
        blinks_processed = []
        if not os.path.exists(self.blinks_dir):
            app_logger.warning(f"Blinks directory not found: {self.blinks_dir}")
            return blinks_processed

        app_logger.debug(f"Scanning blinks directory: {self.blinks_dir}")
        blink_files = [f for f in os.listdir(self.blinks_dir) if f.endswith('.json')]
        app_logger.info(f"Found {len(blink_files)} JSON files in blinks directory.")

        for filename in blink_files:
            blink_id_from_filename = filename.replace('.json','')
            app_logger.debug(f"Processing blink file: {filename} (ID: {blink_id_from_filename})")
            try:
                blink = self.get_blink(blink_id_from_filename, user_id=user_id) # Pass user_id here
                if not blink:
                    app_logger.error(f"Failed to load or process blink from file {filename}. Skipping.")
                    continue

                # get_blink now adds 'interestPercentage' and 'currentUserVoteStatus'
                # It also ensures 'id' is present if data is loaded.
                # We still need to ensure 'publishedAt' for sorting.
                if 'publishedAt' not in blink or not blink['publishedAt']:
                    app_logger.warning(f"Missing 'publishedAt' for blink_id='{blink.get('id')}' in file {filename}. Using fallback date.")
                    blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                # Logging for the item before it's added to the list for sorting
                interest_to_log = blink.get('interestPercentage')
                interest_log_str = f"{interest_to_log:.2f}%" if isinstance(interest_to_log, float) else str(interest_to_log)
                app_logger.debug(
                    f"[GET_ALL_BLINKS_PRE_SORT] ID: {blink.get('id')}, "
                    f"Votes: L={blink.get('votes', {}).get('likes', 0)} / D={blink.get('votes', {}).get('dislikes', 0)}, "
                    f"Interest: {interest_log_str}, "
                    f"Published: {blink.get('publishedAt')}, "
                    f"UserVote: {blink.get('currentUserVoteStatus')}"
                )
                blinks_processed.append(blink)
            except Exception as e:
                app_logger.error(f"Error processing blink file {filename} in get_all_blinks loop: {e}", exc_info=True)

        app_logger.info(f"Sorting {len(blinks_processed)} blinks based on dynamic interest and rules.")
        blinks_processed.sort(key=cmp_to_key(self._compare_blinks))

        app_logger.debug("[GET_ALL_BLINKS_POST_SORT] First 5 items after sorting:")
        for i, sorted_blink in enumerate(blinks_processed[:5]):
            interest_to_log_sorted = sorted_blink.get('interestPercentage')
            interest_log_str_sorted = f"{interest_to_log_sorted:.2f}%" if isinstance(interest_to_log_sorted, float) else str(interest_to_log_sorted)
            app_logger.debug(
                f"  {i+1}. ID: {sorted_blink.get('id')}, "
                f"Interest: {interest_log_str_sorted}, "
                f"Published: {sorted_blink.get('publishedAt')}"
            )

        app_logger.info(f"Successfully processed, loaded and sorted {len(blinks_processed)} blinks.")
        return blinks_processed
