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

# import os # os is already imported by the diagnostic block above
import json
from datetime import datetime, timezone
from functools import cmp_to_key

try:
    from news_blink_backend.src.logger_config import app_logger
    # If import is successful, log this information
    app_logger.info("Successfully imported 'app_logger' from 'news_blink_backend.src.logger_config' in models/news.py.")
except ImportError:
    import logging
    # import os # os is already imported at the top of the file

    # Get the logger for this module (__name__ is 'models.news')
    app_logger = logging.getLogger(__name__) # Or use a specific name like "models.news.fallback"
    app_logger.setLevel(logging.DEBUG)

    # Prevent adding handlers multiple times if this module is reloaded or code runs multiple times
    if not app_logger.handlers:
        # Define the log directory relative to this file (models/news.py)
        # Path: models/news.py -> models/ -> project_root/ -> LOG/
        log_dir_relative_to_this_file = os.path.join(os.path.dirname(__file__), '..', 'LOG')
        log_directory = os.path.abspath(log_dir_relative_to_this_file)

        if not os.path.exists(log_directory):
            try:
                os.makedirs(log_directory)
            except OSError as e:
                # This basic print is a last resort if even logging setup fails for directories
                print(f"CRITICAL: Failed to create log directory {log_directory}. Error: {e}")
                # Fallback to a very basic console logger if directory creation fails
                # so the app doesn't crash due to logging issues.
                ch = logging.StreamHandler()
                ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
                app_logger.addHandler(ch)
                app_logger.error(f"Fallback logger: Directory creation failed for {log_directory}.")


        # Only proceed with file handler if directory exists or was created
        if os.path.exists(log_directory):
            log_file_path = os.path.join(log_directory, "VOTINGPROBLEMLOG.log")

            # File Handler for the fallback logger
            file_handler = logging.FileHandler(log_file_path, mode='a', encoding='utf-8') # 'a' for append
            file_handler.setLevel(logging.DEBUG)

            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(formatter)
            app_logger.addHandler(file_handler)

            # Optional: Add a console handler to this fallback logger as well, for immediate visibility if needed
            # ch_fallback = logging.StreamHandler()
            # ch_fallback.setLevel(logging.INFO) # Or DEBUG
            # ch_fallback.setFormatter(formatter)
            # app_logger.addHandler(ch_fallback)

            app_logger.info(f"Initialized fallback file logger for 'models.news' to: {log_file_path}")
        else:
            # This case means directory creation failed and the earlier print/basic handler took over.
            # Log one more time to the (now basic console) app_logger that file logging is not active.
            app_logger.warning("Directory for VOTINGPROBLEMLOG.log could not be created. Fallback logger is console only.")

    else: # This means handlers were already added to this specific logger instance
        app_logger.info(f"Handlers already configured for logger '{app_logger.name}'. Skipping fallback setup.")

    # The original warning about failing to import the main logger is still good.
    app_logger.warning("Failed to import 'app_logger' from 'news_blink_backend.src.logger_config'. Using fallback logger for 'models.news'.")

import logging # Ensure logging is imported for getLogger
vote_fix_logger_model_level = logging.getLogger('VoteFixLogLogger') # Define once at model level if preferred, or locally in methods

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
        # Log only a subset of blink_data for brevity, e.g., id, title, votes
        log_data_subset = {
            'id': blink_data.get('id'),
            'title': blink_data.get('title_for_logging', blink_data.get('title', 'N/A')[:50]), # Avoid overly long titles in logs
            'votes': blink_data.get('votes'),
            'user_votes': blink_data.get('user_votes') # Added for vote context
        }
        # Specific log for VoteFixLog when saving related to votes
        # This requires context; let's assume if 'user_votes' is present and non-empty, it might be vote related.
        # A more robust way would be a flag passed to save_blink if the save is due to a vote.
        if blink_data.get('user_votes'): # Heuristic: if user_votes are present, it might be relevant
            vote_fix_logger_model_level.info(f"Saving blink_id='{blink_id}' (potentially after vote). Votes: {log_data_subset.get('votes')}, UserVotes sample: {list(log_data_subset.get('user_votes', {}).items())[:2]}")

        app_logger.debug(f"Attempting to save blink_id='{blink_id}' to {filepath}. Data subset: {json.dumps(log_data_subset)}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blink_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved blink_id='{blink_id}' to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving blink_id='{blink_id}' to {filepath}: {e}", exc_info=True)
            raise

    def get_blink(self, blink_id, user_id=None): # Added user_id parameter
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.debug(f"Attempting to get blink_id='{blink_id}' from {filepath} for user_id='{user_id}'")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Ensure votes structure is initialized (already updated in Step 1)
                data.setdefault('votes', {}).setdefault('likes', 0)
                data['votes'].setdefault('dislikes', 0)
                data.setdefault('user_votes', {}) # Ensure user_votes exists

                # Add currentUserVoteStatus
                if user_id:
                    data['currentUserVoteStatus'] = self._get_user_vote_status(data, user_id)
                    # Specific log for VoteFixLog when getting blink for a user (likely for voting/display)
                    vote_fix_logger_model_level.info(f"get_blink for voting/display: id='{blink_id}', user_id='{user_id}'. Votes: {data.get('votes')}, UserVotes: {data.get('user_votes', {}).get(user_id, 'N/A')}, Determined status: {data['currentUserVoteStatus']}")
                else:
                    data['currentUserVoteStatus'] = None
                    # Log for general purpose when no user_id is present
                    vote_fix_logger_model_level.debug(f"get_blink for general purpose: id='{blink_id}', no user_id. Votes: {data.get('votes')}")

                # Calculate and add interestPercentage for consistency - MOVED INSIDE TRY
                data['interestPercentage'] = self.calculate_interest_percentage(data)
                app_logger.debug(f"Successfully loaded blink_id='{blink_id}'. Votes: {data.get('votes')}, UserVote: {data.get('currentUserVoteStatus')}, Interest: {data.get('interestPercentage')}")
                return data # This is the return for the successful try block
            except Exception as e:
                app_logger.error(f"Error reading or processing blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
                # Optionally, add a VoteFixLogLogger error here too if this specific log file needs to capture this error
                vote_fix_logger_model_level.error(f"Error reading or processing blink_id='{blink_id}' in get_blink: {e}", exc_info=True)
                # For an exception during processing, we fall through to the final 'return None'
        else: # This corresponds to 'if os.path.exists(filepath):'
            app_logger.warning(f"Blink file not found for blink_id='{blink_id}' at {filepath}")

        return None # Common return for file not found or exception during processing

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
                # Ensure votes structure exists, using likes/dislikes
                votes = data.setdefault('votes', {})
                votes.setdefault('likes', 0)
                votes.setdefault('dislikes', 0)
                data.setdefault('user_votes', {}) # Ensure user_votes structure exists
                app_logger.debug(f"Successfully loaded article_id='{article_id}'")
                return data
            except Exception as e:
                app_logger.error(f"Error reading article_id='{article_id}' from {filepath}: {e}", exc_info=True)
        else:
            app_logger.warning(f"Article file not found for article_id='{article_id}' at {filepath}")
        return None

    def process_user_vote(self, blink_id, user_id, vote_type, previous_vote):
        """
        Processes a user's vote on a blink, expecting 'like'/'dislike' terminology.
        """
        vote_fix_logger = logging.getLogger('VoteFixLogLogger')
        vote_fix_logger.info(f"process_user_vote entry: blink_id='{blink_id}', user_id='{user_id}', vote_type='{vote_type}', previous_vote='{previous_vote}'")
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.info(f"process_user_vote: blink_id='{blink_id}', user_id='{user_id}', vote_type='{vote_type}', previous_vote='{previous_vote}'")

        if not os.path.exists(filepath):
            app_logger.warning(f"process_user_vote: Blink file not found for blink_id='{blink_id}' at {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                article_data = json.load(f)
        except (IOError, json.JSONDecodeError) as e:
            app_logger.error(f"process_user_vote: Error reading or decoding blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
            return None

        article_data.setdefault('votes', {})
        likes = article_data['votes'].get('likes', 0)
        dislikes = article_data['votes'].get('dislikes', 0)
        user_votes_map = article_data.setdefault('user_votes', {}) # Ensures user_votes exists and get a reference

        server_known_user_vote = user_votes_map.get(user_id) # This is the true previous vote from server's perspective

        # Log client's intention and server's known state for context
        app_logger.debug(f"Vote context for blink {blink_id}, user {user_id}: Client vote_type='{vote_type}', client_previous_vote='{previous_vote}', server_known_user_vote='{server_known_user_vote}'")
        vote_fix_logger.info(f"Initial state for {blink_id}: Likes={likes}, Dislikes={dislikes}. User '{user_id}' server_known_vote: {server_known_user_vote}")

        action_taken_log = "No change initially." # Using variable name from pseudocode

        if server_known_user_vote == vote_type:  # User clicked an already active button
            if vote_type == 'like':
                likes = max(0, likes - 1)
                action_taken_log = f"User '{user_id}' UNLIKED."
            elif vote_type == 'dislike':
                dislikes = max(0, dislikes - 1)
                action_taken_log = f"User '{user_id}' UNDISLIKED."
            user_votes_map.pop(user_id, None)

        elif server_known_user_vote is None:  # New vote by the user
            if vote_type == 'like':
                likes += 1
                action_taken_log = f"User '{user_id}' NEWLY LIKED."
            elif vote_type == 'dislike':
                dislikes += 1 # Corrected: This MUST be increment for a new dislike
                action_taken_log = f"User '{user_id}' NEWLY DISLIKED."
            user_votes_map[user_id] = vote_type

        else:  # User is switching their vote
            if vote_type == 'like':  # Switching to 'like' (must have been 'dislike' previously)
                likes += 1
                dislikes = max(0, dislikes - 1)
                action_taken_log = f"User '{user_id}' SWITCHED vote from DISLIKE to LIKE."
            elif vote_type == 'dislike':  # Switching to 'dislike' (must have been 'like' previously)
                dislikes += 1 # Corrected: This MUST be increment for switching to a dislike
                likes = max(0, likes - 1)
                action_taken_log = f"User '{user_id}' SWITCHED vote from LIKE to DISLIKE."
            user_votes_map[user_id] = vote_type

        # Update article_data with new likes, dislikes, and user_votes_map
        article_data['votes']['likes'] = likes
        article_data['votes']['dislikes'] = dislikes
        article_data['user_votes'] = user_votes_map # Assign back, user_votes_map was a new dict from setdefault if key missing

        # Detailed logging BEFORE saving the file, including the client's original previous_vote for context
        app_logger.info(
            f"Vote processed for blink {blink_id} by user {user_id}. "
            f"Action: {action_taken_log}. "
            f"Final Counts: Likes={likes}, Dislikes={dislikes}. "
            f"User vote status in map: {user_votes_map.get(user_id)}. "
            f"Client's intended vote_type: {vote_type}, " # This is the current vote action from client
            f"Client's stated previous vote: {previous_vote}, " # This is what client thought its vote was
            f"Server's actual previous vote for user: {server_known_user_vote}."
        )
        # vote_fix_logger can have a similar detailed message or focus on specific aspects
        vote_fix_logger.info(f"Vote for {blink_id}, user {user_id}: {action_taken_log}. L/D: {likes}/{dislikes}. User map now: {user_votes_map.get(user_id)}. Client previous: {previous_vote}, Server previous: {server_known_user_vote}")

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"process_user_vote: Successfully saved updated blink_id='{blink_id}' to {filepath}")
            vote_fix_logger.info(f"Successfully saved blink_id='{blink_id}' after vote processing.")
        except IOError as e:
            vote_fix_logger.error(f"IOError saving blink_id='{blink_id}' in process_user_vote: {e}", exc_info=True)
            app_logger.error(f"process_user_vote: IOError saving blink_id='{blink_id}' to {filepath}: {e}", exc_info=True)
            return None

        # Sync with full article file if it exists
        try:
            full_article_path = os.path.join(self.articles_dir, f"{blink_id}.json")
            if os.path.exists(full_article_path):
                with open(full_article_path, 'r', encoding='utf-8') as f:
                    full_article_data = json.load(f)
                full_article_data['votes'] = article_data['votes'].copy()
                full_article_data['user_votes'] = article_data['user_votes'].copy()
                with open(full_article_path, 'w', encoding='utf-8') as f:
                    json.dump(full_article_data, f, ensure_ascii=False, indent=2)
                app_logger.debug(f"process_user_vote: Synced votes to full article file for blink_id='{blink_id}'.")
        except Exception as e:
            app_logger.warning(f"process_user_vote: Non-critical error syncing votes to full article for blink_id='{blink_id}': {e}", exc_info=True)

        article_data['currentUserVoteStatus'] = article_data['user_votes'].get(user_id) # Reflects the current state of the vote for this user
        # Calculate and include interestPercentage in the returned data
        article_data['interestPercentage'] = self.calculate_interest_percentage(article_data)
        app_logger.info(f"process_user_vote: Returning updated data for blink_id='{blink_id}' with interestPercentage={article_data['interestPercentage']:.2f}%")
        return article_data

    def _get_user_vote_status(self, blink_data, user_id):
        if not isinstance(blink_data, dict):
            app_logger.warning(f"_get_user_vote_status: blink_data is not a dictionary for user_id='{user_id}'.")
            return None
        # user_votes now stores 'like' or 'dislike'
        status = blink_data.get('user_votes', {}).get(user_id)
        app_logger.debug(f"_get_user_vote_status: For user_id='{user_id}', vote_status='{status}'.")
        return status

    def calculate_interest_percentage(self, blink_data): # Removed confidence_factor_c
        vote_fix_logger = logging.getLogger('VoteFixLogLogger') # Ensure logger is obtained
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
            interest = 50.0  # User-specified default for no votes
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
        # vote_fix_logger can be used here if detailed per-comparison logging is needed.
        # For brevity, primary logging is via app_logger or high-level vote_fix_logger.

        # Helper for parsing datetime, ensuring it's robust
        def parse_datetime_for_compare(published_at_str):
            if not published_at_str: # Handles None or empty strings
                return datetime.min.replace(tzinfo=timezone.utc)
            try:
                dt = datetime.fromisoformat(str(published_at_str).replace('Z', '+00:00'))
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, TypeError):
                app_logger.warning(f"Could not parse datetime string '{published_at_str}' in _compare_blinks. Using fallback minimum date.", exc_info=False) # exc_info=False to reduce noise for common parsing issues
                return datetime.min.replace(tzinfo=timezone.utc)

        # 1. Interest (desc)
        interest_a = blink_a.get('interestPercentage', 0.0)
        interest_b = blink_b.get('interestPercentage', 0.0)
        if interest_a != interest_b:
            return -1 if interest_a > interest_b else 1

        # 2. Likes (desc)
        likes_a = blink_a.get('votes', {}).get('likes', 0)
        likes_b = blink_b.get('votes', {}).get('likes', 0)
        if likes_a != likes_b:
            return -1 if likes_a > likes_b else 1

        # 3. Publication Date (desc) - using 'publishedAt' as per original example
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
                blink = self.get_blink(blink_id_from_filename) # get_blink now ensures votes.likes/dislikes exist
                if not blink:
                    app_logger.error(f"Failed to load or process blink from file {filename}. Skipping.")
                    continue

                blink.setdefault('id', blink_id_from_filename)
                # current_votes are already initialized by get_blink if file exists and is readable
                # current_votes = blink['votes'] # Not strictly needed here if get_blink populated it

                if 'publishedAt' not in blink or not blink['publishedAt']: # 'publishedAt' is used in _compare_blinks
                    app_logger.warning(f"Missing 'publishedAt' for blink_id='{blink.get('id')}' in file {filename}. Using fallback date.")
                    blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                # Calculate and store interestPercentage using the simplified method
                blink['interestPercentage'] = self.calculate_interest_percentage(blink)

                if user_id:
                    blink['currentUserVoteStatus'] = self._get_user_vote_status(blink, user_id)
                else:
                    blink['currentUserVoteStatus'] = None

                # Refined logging for interest percentage
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
                # Original log below can be kept or removed if the new one is sufficient
                # app_logger.debug(f"Processed blink_id='{blink.get('id')}': UserVote='{blink['currentUserVoteStatus']}', Votes(L/D): {current_votes.get('likes',0)}/{current_votes.get('dislikes',0)}, Interest: {blink.get('interestPercentage', 'N/A')}")
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
