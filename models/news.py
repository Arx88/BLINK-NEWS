import os
import json
from datetime import datetime, timezone
from functools import cmp_to_key

try:
    from news_blink_backend.src.logger_config import app_logger
except ImportError:
    import logging
    app_logger = logging.getLogger(__name__)
    app_logger.setLevel(logging.DEBUG)
    if not app_logger.hasHandlers():
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        app_logger.addHandler(ch)
    app_logger.warning("Failed to import app_logger from news_blink_backend.src.logger_config. Using fallback basic logger for models.news.")

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
            'votes': blink_data.get('votes')
        }
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
                else:
                    data['currentUserVoteStatus'] = None

                app_logger.debug(f"Successfully loaded blink_id='{blink_id}'. Votes: {data.get('votes')}, UserVote: {data.get('currentUserVoteStatus')}")
                return data
            except Exception as e:
                app_logger.error(f"Error reading blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
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

        app_logger.debug(f"process_user_vote: Current votes for {blink_id}: L={likes}, D={dislikes}. User's previous vote: '{previous_vote}'")

        vote_changed_or_new = False
        if previous_vote == vote_type: # User clicked the same button again
            app_logger.info(f"process_user_vote: User '{user_id}' re-voted '{vote_type}' for blink_id='{blink_id}'. No change in vote counts or user_vote record.")
            # Vote does not change, user_vote record also does not change.
        elif previous_vote is None:
            if vote_type == 'like':
                likes += 1
            elif vote_type == 'dislike': # Assuming vote_type must be 'like' or 'dislike' by now
                dislikes += 1
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
        elif previous_vote == 'like' and vote_type == 'dislike':
            likes = max(0, likes - 1)
            dislikes += 1
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
        elif previous_vote == 'dislike' and vote_type == 'like':
            dislikes = max(0, dislikes - 1)
            likes += 1
            article_data['user_votes'][user_id] = vote_type
            vote_changed_or_new = True
        # Case: User explicitly removes their vote by voting for the same type again (e.g. from "like" to "neutral")
        # This case is handled by `previous_vote == vote_type` if the API sends the *same* voteType to signify removal.
        # If API sends a *different* signal for removal (e.g. vote_type=None or 'neutral'), more logic is needed here.
        # Based on current prompt, "previous_vote == vote_type means user clicked same button again", implies no removal logic by re-clicking.
        # If the intention is that re-clicking removes the vote, the logic for previous_vote == vote_type should be:
        # if vote_type == 'like': likes = max(0, likes - 1)
        # elif vote_type == 'dislike': dislikes = max(0, dislikes - 1)
        # del article_data['user_votes'][user_id]
        # vote_changed_or_new = True
        # current_vote_for_user_response = None # vote removed

        if vote_changed_or_new:
             app_logger.info(f"process_user_vote: Vote change for blink_id='{blink_id}', user_id='{user_id}'. From '{previous_vote}' to '{vote_type}'. New counts L/D: {likes}/{dislikes}")

        article_data['votes']['likes'] = likes
        article_data['votes']['dislikes'] = dislikes

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"process_user_vote: Successfully saved updated blink_id='{blink_id}' to {filepath}")
        except IOError as e:
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
        if not isinstance(blink_data, dict) or 'votes' not in blink_data:
            app_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes'. ID: {blink_data.get('id', 'N/A')}. Returning 0.0 interest.")
            return 0.0

        current_votes = blink_data['votes']
        # Use 'likes' and 'dislikes'
        likes = current_votes.get('likes', 0)
        dislikes = current_votes.get('dislikes', 0)

        total_votes = likes + dislikes
        net_vote_difference = likes - dislikes # Standard: positive - negative

        if total_votes == 0:
            interest = 0.0
        else:
            interest = (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0

        app_logger.debug(f"calculate_interest_percentage for ID {blink_data.get('id', 'N/A')}: L={likes}, D={dislikes}, Total={total_votes}, NetDiff={net_vote_difference}, C={confidence_factor_c} -> Interest={interest:.2f}%")
        return interest

    def _compare_blinks(self, blink_a, blink_b):
        # Helper to parse 'publishedAt' safely
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

        # Compare interestPercentage (descending)
        if interest_a > interest_b:
            # app_logger.debug(f"Sort: {blink_a.get('id')} ({interest_a}%) > {blink_b.get('id')} ({interest_b}%) by interest.")
            return -1
        if interest_a < interest_b:
            # app_logger.debug(f"Sort: {blink_a.get('id')} ({interest_a}%) < {blink_b.get('id')} ({interest_b}%) by interest.")
            return 1

        # app_logger.debug(f"Sort: Interest tied for {blink_a.get('id')} and {blink_b.get('id')} ({interest_a}%). Proceeding to tie-breakers.")

        # If interestPercentage is tied, parse publishedAt dates
        # These are parsed early as they are used in multiple rules or as a final tie-breaker
        date_a = parse_datetime(blink_a.get('publishedAt'))
        date_b = parse_datetime(blink_b.get('publishedAt'))

        # Ensure votes structure and default likes/dislikes
        votes_a = blink_a.get('votes', {})
        likes_a = votes_a.get('likes', 0)
        dislikes_a = votes_a.get('dislikes', 0)

        votes_b = blink_b.get('votes', {})
        likes_b = votes_b.get('likes', 0)
        dislikes_b = votes_b.get('dislikes', 0)

        # Regla A (Noticias sin votos)
        # A blink qualifies if it has 0 interest (already established by tie), 0 likes, and 0 dislikes.
        is_rule_a_candidate_a = (likes_a == 0 and dislikes_a == 0) # interest_a == 0.0 is implicit due to tie
        is_rule_a_candidate_b = (likes_b == 0 and dislikes_b == 0) # interest_b == 0.0 is implicit

        if interest_a == 0.0: # This check ensures Rule A is only applied when common interest is truly zero
            if is_rule_a_candidate_a and not is_rule_a_candidate_b:
                # app_logger.debug(f"Sort Rule A: {blink_a.get('id')} (no votes) vs {blink_b.get('id')} (has votes/activity). A comes first.")
                return -1 # A qualifies for Rule A and B doesn't (B might have votes but still 0 interest)
            if not is_rule_a_candidate_a and is_rule_a_candidate_b:
                # app_logger.debug(f"Sort Rule A: {blink_a.get('id')} (has votes/activity) vs {blink_b.get('id')} (no votes). B comes first.")
                return 1  # B qualifies for Rule A and A doesn't
            if is_rule_a_candidate_a and is_rule_a_candidate_b:
                # Both qualify for Rule A (0 interest, 0 likes, 0 dislikes), sort by publishedAt (descending)
                # app_logger.debug(f"Sort Rule A (Both): {blink_a.get('id')} vs {blink_b.get('id')}. Comparing dates: {date_a} vs {date_b}.")
                if date_a > date_b: return -1
                if date_a < date_b: return 1
                # app_logger.debug(f"Sort Rule A (Both): Dates tied for {blink_a.get('id')} and {blink_b.get('id')}. Proceeding.")
                # Fall through to default date comparison if dates are identical, though unlikely for different blinks

        # Regla B (Noticias con 0 positivos y varios negativos)
        # This rule applies if items are tied by interestPercentage (which they are at this point).
        # A blink qualifies if it has 0 likes and >0 dislikes.
        is_rule_b_candidate_a = (likes_a == 0 and dislikes_a > 0)
        is_rule_b_candidate_b = (likes_b == 0 and dislikes_b > 0)

        if is_rule_b_candidate_a and is_rule_b_candidate_b:
            # Both qualify for Rule B, compare dislikes (ascending - fewer dislikes is better)
            # app_logger.debug(f"Sort Rule B (Both): {blink_a.get('id')} ({dislikes_a} dislikes) vs {blink_b.get('id')} ({dislikes_b} dislikes). Comparing dislikes.")
            if dislikes_a < dislikes_b: return -1
            if dislikes_a > dislikes_b: return 1
            # app_logger.debug(f"Sort Rule B (Both): Dislikes tied for {blink_a.get('id')} and {blink_b.get('id')}. Proceeding to date tie-breaker.")
            # If dislikes are also tied, fall through to default date comparison

        # Default Tie-Breaker: Compare by publishedAt (descending)
        # app_logger.debug(f"Sort Default Tie-Break: {blink_a.get('id')} vs {blink_b.get('id')}. Comparing dates: {date_a} vs {date_b}.")
        if date_a > date_b: return -1
        if date_a < date_b: return 1

        # app_logger.debug(f"Sort Ultimate Tie: {blink_a.get('id')} vs {blink_b.get('id')}. IDs: {blink_a.get('id')} vs {blink_b.get('id')}. Considered equal.")
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
