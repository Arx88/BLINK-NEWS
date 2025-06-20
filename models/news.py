import os
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

                app_logger.debug(f"Successfully loaded blink_id='{blink_id}'. Votes: {data.get('votes')}, UserVote: {data.get('currentUserVoteStatus')}")
                return data
            except Exception as e:
                app_logger.error(f"Error reading or processing blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
                # Optionally, add a VoteFixLogLogger error here too if this specific log file needs to capture this error
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
        article_data.setdefault('user_votes', {})
        vote_fix_logger.info(f"Initial votes for {blink_id}: Likes={likes}, Dislikes={dislikes}. User's current vote in user_votes: {article_data['user_votes'].get(user_id)}")

        app_logger.debug(f"process_user_vote: Current votes for {blink_id}: L={likes}, D={dislikes}. User's previous vote: '{previous_vote}'")

        vote_changed_or_new = False
        action_description = "No change: user re-clicked same vote type."
        if previous_vote == vote_type: # User clicked the same button again
            app_logger.info(f"process_user_vote: User '{user_id}' re-voted '{vote_type}' for blink_id='{blink_id}'. No change in vote counts or user_vote record.")
            # Vote does not change, user_vote record also does not change.
        elif previous_vote is None:
            if vote_type == 'like':
                likes += 1
                action_description = f"New vote: user '{user_id}' liked."
            elif vote_type == 'dislike':
                dislikes += 1
                action_description = f"New vote: user '{user_id}' disliked."
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
        elif previous_vote == 'like' and vote_type == 'dislike':
            likes = max(0, likes - 1)
            dislikes += 1
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
            action_description = f"Vote change: user '{user_id}' changed from like to dislike."
        elif previous_vote == 'dislike' and vote_type == 'like':
            dislikes = max(0, dislikes - 1)
            likes += 1
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
            action_description = f"Vote change: user '{user_id}' changed from dislike to like."

        vote_fix_logger.info(f"Vote processing for {blink_id}, user '{user_id}': {action_description}")

        if vote_changed_or_new:
             app_logger.info(f"process_user_vote: Vote change for blink_id='{blink_id}', user_id='{user_id}'. From '{previous_vote}' to '{vote_type}'. New counts L/D: {likes}/{dislikes}")
             vote_fix_logger.info(f"Updated vote counts for {blink_id}: Likes={likes}, Dislikes={dislikes}. User '{user_id}' vote set to: {article_data['user_votes'].get(user_id)}")

        article_data['votes']['likes'] = likes
        article_data['votes']['dislikes'] = dislikes

        vote_fix_logger.info(f"Before saving {blink_id}: Likes={article_data['votes']['likes']}, Dislikes={article_data['votes']['dislikes']}, User vote for {user_id}: {article_data['user_votes'].get(user_id)}")
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
        return article_data

    def _get_user_vote_status(self, blink_data, user_id):
        if not isinstance(blink_data, dict):
            app_logger.warning(f"_get_user_vote_status: blink_data is not a dictionary for user_id='{user_id}'.")
            return None
        # user_votes now stores 'like' or 'dislike'
        status = blink_data.get('user_votes', {}).get(user_id)
        app_logger.debug(f"_get_user_vote_status: For user_id='{user_id}', vote_status='{status}'.")
        return status

    def calculate_interest_percentage(self, blink_data, confidence_factor_c=5):
        vote_fix_logger = logging.getLogger('VoteFixLogLogger')
        blink_id_for_log = blink_data.get('id', 'N/A') if isinstance(blink_data, dict) else 'N/A'
        current_likes_for_log = blink_data.get('votes', {}).get('likes', 0) if isinstance(blink_data, dict) else 0
        current_dislikes_for_log = blink_data.get('votes', {}).get('dislikes', 0) if isinstance(blink_data, dict) else 0
        vote_fix_logger.info(f"calculate_interest_percentage entry: blink_id='{blink_id_for_log}', current_likes={current_likes_for_log}, current_dislikes={current_dislikes_for_log}, C={confidence_factor_c}")

        if not isinstance(blink_data, dict) or 'votes' not in blink_data:
            app_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes'. ID: {blink_id_for_log}. Returning 0.0 interest.")
            vote_fix_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes' for ID='{blink_id_for_log}'. Returning 0.0.")
            return 0.0

        current_votes = blink_data['votes']
        likes = current_votes.get('likes', 0)
        dislikes = current_votes.get('dislikes', 0)

        total_votes = likes + dislikes
        net_vote_difference = likes - dislikes

        vote_fix_logger.debug(f"calculate_interest_percentage ({blink_id_for_log}): Likes={likes}, Dislikes={dislikes}, TotalVotes={total_votes}, NetVoteDiff={net_vote_difference}")

        if total_votes == 0:
            interest = 0.0
        else:
            # Original formula: (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0
            # Corrected based on api.py: (likes / total_votes) * 100.0 if total_votes > 0, else 50.0
            # Sticking to formula in this file, as subtask is about logging this file's logic.
            # The api.py calculate_interest is different.
            interest = (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0


        app_logger.debug(f"calculate_interest_percentage for ID {blink_id_for_log}: L={likes}, D={dislikes}, Total={total_votes}, NetDiff={net_vote_difference}, C={confidence_factor_c} -> Interest={interest:.2f}%")
        vote_fix_logger.info(f"calculate_interest_percentage result for ID='{blink_id_for_log}': Calculated Interest={interest:.2f}%")
        return interest

    def _compare_blinks(self, blink_a, blink_b):
        vote_fix_logger = logging.getLogger('VoteFixLogLogger')
        # Prepare summaries for logging
        summary_a = {
            'id': blink_a.get('id', 'N/A'), 'interestP': blink_a.get('interestPercentage', 0.0),
            'likes': blink_a.get('votes', {}).get('likes', 0), 'date': blink_a.get('publishedAt', 'N/A')
        }
        summary_b = {
            'id': blink_b.get('id', 'N/A'), 'interestP': blink_b.get('interestPercentage', 0.0),
            'likes': blink_b.get('votes', {}).get('likes', 0), 'date': blink_b.get('publishedAt', 'N/A')
        }
        vote_fix_logger.debug(f"_compare_blinks entry: Blink A summary: {summary_a}, Blink B summary: {summary_b}")

        def parse_datetime(published_at_str):
            try:
                # Attempt to parse ISO format, common in JSON. Handle 'Z' for UTC.
                dt = datetime.fromisoformat(published_at_str.replace('Z', '+00:00'))
                # Ensure datetime is timezone-aware, defaulting to UTC if naive.
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return dt
            except (ValueError, AttributeError, TypeError): # TypeError if not string, AttributeError if methods like .replace fail
                app_logger.warning(f"Could not parse datetime string '{published_at_str}'. Using fallback minimum date.", exc_info=True)
                return datetime.min.replace(tzinfo=timezone.utc)

        # Retrieve interestPercentage, default to 0.0 if missing
        interest_a = blink_a.get('interestPercentage', 0.0)
        interest_b = blink_b.get('interestPercentage', 0.0)
        vote_fix_logger.debug(f"Comparing interest: A({summary_a['id']})={interest_a:.2f}%, B({summary_b['id']})={interest_b:.2f}%")

        if interest_a > interest_b:
            vote_fix_logger.debug(f"Outcome: A > B by interest ({interest_a:.2f}% > {interest_b:.2f}%)")
            return -1
        if interest_a < interest_b:
            vote_fix_logger.debug(f"Outcome: A < B by interest ({interest_a:.2f}% < {interest_b:.2f}%)")
            return 1

        vote_fix_logger.debug(f"Interest tied at {interest_a:.2f}%. Proceeding to tie-breakers.")
        date_a = parse_datetime(blink_a.get('publishedAt'))
        date_b = parse_datetime(blink_b.get('publishedAt'))

        votes_a_data = blink_a.get('votes', {})
        likes_a = votes_a_data.get('likes', 0)
        dislikes_a = votes_a_data.get('dislikes', 0)
        votes_b_data = blink_b.get('votes', {})
        likes_b = votes_b_data.get('likes', 0)
        dislikes_b = votes_b_data.get('dislikes', 0)
        vote_fix_logger.debug(f"Tie-breaker data: A_likes={likes_a}, A_dislikes={dislikes_a}, A_date={date_a.isoformat()}; B_likes={likes_b}, B_dislikes={dislikes_b}, B_date={date_b.isoformat()}")

        is_rule_a_candidate_a = (likes_a == 0 and dislikes_a == 0)
        is_rule_a_candidate_b = (likes_b == 0 and dislikes_b == 0)

        if interest_a == 0.0:
            vote_fix_logger.debug("Common interest is 0.0, evaluating Rule A (no votes).")
            if is_rule_a_candidate_a and not is_rule_a_candidate_b:
                vote_fix_logger.debug("Outcome Rule A: A (no votes) > B (has activity).")
                return -1
            if not is_rule_a_candidate_a and is_rule_a_candidate_b:
                vote_fix_logger.debug("Outcome Rule A: A (has activity) < B (no votes).")
                return 1
            if is_rule_a_candidate_a and is_rule_a_candidate_b:
                vote_fix_logger.debug("Rule A (Both no votes): Comparing dates. A_date vs B_date.")
                if date_a > date_b: vote_fix_logger.debug("Outcome Rule A (Both): A > B by date."); return -1
                if date_a < date_b: vote_fix_logger.debug("Outcome Rule A (Both): A < B by date."); return 1
                vote_fix_logger.debug("Rule A (Both): Dates tied.")

        is_rule_b_candidate_a = (likes_a == 0 and dislikes_a > 0)
        is_rule_b_candidate_b = (likes_b == 0 and dislikes_b > 0)
        vote_fix_logger.debug(f"Rule B check (0 likes, >0 dislikes): A_candidate={is_rule_b_candidate_a}, B_candidate={is_rule_b_candidate_b}")
        if is_rule_b_candidate_a and is_rule_b_candidate_b:
            vote_fix_logger.debug("Rule B (Both 0 likes, >0 dislikes): Comparing dislikes (ascending). A_dislikes vs B_dislikes.")
            if dislikes_a < dislikes_b: vote_fix_logger.debug(f"Outcome Rule B (Both): A ({dislikes_a}) < B ({dislikes_b}) by dislikes (fewer is better)."); return -1
            if dislikes_a > dislikes_b: vote_fix_logger.debug(f"Outcome Rule B (Both): A ({dislikes_a}) > B ({dislikes_b}) by dislikes."); return 1
            vote_fix_logger.debug("Rule B (Both): Dislikes tied.")
        # Note: Original logic did not have specific outcomes if only one candidate met Rule B and the other didn't (but wasn't Rule A either)
        # The current logic falls through to date comparison if Rule B doesn't resolve for two candidates.

        vote_fix_logger.debug("Default Tie-Breaker: Comparing dates (descending). A_date vs B_date.")
        if date_a > date_b: vote_fix_logger.debug("Outcome Default: A > B by date."); return -1
        if date_a < date_b: vote_fix_logger.debug("Outcome Default: A < B by date."); return 1

        vote_fix_logger.debug(f"Ultimate Tie: A ({summary_a['id']}) and B ({summary_b['id']}) considered equal.")
        return 0

    def get_all_blinks(self, user_id=None):
        app_logger.info(f"get_all_blinks called. user_id='{user_id}'")
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
                current_votes = blink['votes'] # Already uses likes/dislikes due to get_blink

                if 'publishedAt' not in blink or not blink['publishedAt']:
                    app_logger.warning(f"Missing 'publishedAt' for blink_id='{blink.get('id')}' in file {filename}. Using fallback date.")
                    blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                # Calculate and store interestPercentage
                blink['interestPercentage'] = self.calculate_interest_percentage(blink, confidence_factor_c=5)

                if user_id:
                    blink['currentUserVoteStatus'] = self._get_user_vote_status(blink, user_id) # Uses like/dislike now
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
