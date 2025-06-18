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

    def get_blink(self, blink_id):
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.debug(f"Attempting to get blink_id='{blink_id}' from {filepath}")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                converted_keys = False
                if 'votes' in data and isinstance(data['votes'], dict):
                    if 'likes' in data['votes']:
                        data['votes']['positive'] = data['votes'].pop('likes')
                        converted_keys = True
                    if 'dislikes' in data['votes']:
                        data['votes']['negative'] = data['votes'].pop('dislikes')
                        converted_keys = True
                if converted_keys:
                     app_logger.info(f"Converted votes from likes/dislikes to positive/negative for blink_id='{blink_id}' during get_blink.")

                app_logger.debug(f"Successfully loaded blink_id='{blink_id}'. Votes: {data.get('votes')}")
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

                converted_keys = False
                if 'votes' in data and isinstance(data['votes'], dict):
                    if 'likes' in data['votes']:
                        data['votes']['positive'] = data['votes'].pop('likes')
                        converted_keys = True
                    if 'dislikes' in data['votes']:
                        data['votes']['negative'] = data['votes'].pop('dislikes')
                        converted_keys = True
                if converted_keys:
                    app_logger.info(f"Converted votes for article_id='{article_id}' during get_article.")

                app_logger.debug(f"Successfully loaded article_id='{article_id}'")
                return data
            except Exception as e:
                app_logger.error(f"Error reading article_id='{article_id}' from {filepath}: {e}", exc_info=True)
        else:
            app_logger.warning(f"Article file not found for article_id='{article_id}' at {filepath}")
        return None

    def process_vote(self, article_id, user_id, new_vote_type):
        app_logger.info(f"Processing vote: article_id='{article_id}', user_id='{user_id}', new_vote_type='{new_vote_type}'")
        blink = self.get_blink(article_id)
        if not blink:
            app_logger.warning(f"process_vote: Blink not found for article_id='{article_id}'. Cannot process vote.")
            return None

        current_votes = blink.setdefault('votes', {})
        current_votes.setdefault('positive', 0)
        current_votes.setdefault('negative', 0)

        blink.setdefault('user_votes', {})

        if 'publishedAt' not in blink or not blink['publishedAt']:
            app_logger.warning(f"process_vote: Missing 'publishedAt' for article_id='{article_id}'. Setting to current UTC time.")
            blink['publishedAt'] = datetime.now(timezone.utc).isoformat()

        previous_user_vote = blink['user_votes'].get(user_id)
        app_logger.debug(f"process_vote: article_id='{article_id}', user_id='{user_id}'. Previous vote: '{previous_user_vote}', New vote: '{new_vote_type}'. Current total votes: P={current_votes['positive']}, N={current_votes['negative']}")

        original_positive = current_votes['positive']
        original_negative = current_votes['negative']

        if previous_user_vote == new_vote_type:
            app_logger.info(f"process_vote: User '{user_id}' re-voted '{new_vote_type}' for article_id='{article_id}'. No change in vote counts.")
        else:
            if previous_user_vote == 'positive':
                current_votes['positive'] = max(0, current_votes['positive'] - 1)
            elif previous_user_vote == 'negative':
                current_votes['negative'] = max(0, current_votes['negative'] - 1)

            if new_vote_type == 'positive':
                current_votes['positive'] += 1
            elif new_vote_type == 'negative':
                current_votes['negative'] += 1

            blink['user_votes'][user_id] = new_vote_type
            app_logger.info(f"process_vote: Vote changed for article_id='{article_id}', user_id='{user_id}'. From '{previous_user_vote}' to '{new_vote_type}'. "
                            f"Vote counts changed from P={original_positive}, N={original_negative} to P={current_votes['positive']}, N={current_votes['negative']}.")

        try:
            self.save_blink(article_id, blink)
        except Exception:
            app_logger.error(f"process_vote: Critical failure saving blink_id='{article_id}' after vote. Vote processing aborted.")
            return None

        try:
            article_data_to_sync = self.get_article(article_id)
            if article_data_to_sync:
                app_logger.debug(f"process_vote: Syncing votes for full article_id='{article_id}'.")
                article_data_to_sync.setdefault('votes', {}).update(current_votes) # Use current_votes which is blink['votes']
                article_data_to_sync.setdefault('user_votes', {}).update(blink['user_votes'])
                self.save_article(article_id, article_data_to_sync)
        except Exception as e:
            app_logger.warning(f"process_vote: Non-critical error syncing votes to full article_id='{article_id}': {e}", exc_info=True)

        app_logger.debug(f"process_vote completed for article_id='{article_id}'. Returning updated blink.")
        return blink

    def _get_user_vote_status(self, blink_data, user_id):
        if not isinstance(blink_data, dict):
            app_logger.warning(f"_get_user_vote_status: blink_data is not a dictionary for user_id='{user_id}'.")
            return None
        status = blink_data.get('user_votes', {}).get(user_id)
        app_logger.debug(f"_get_user_vote_status: For user_id='{user_id}', vote_status='{status}'.")
        return status

    def calculate_interest_percentage(self, blink_data, confidence_factor_c=5):
        if not isinstance(blink_data, dict) or 'votes' not in blink_data: # get_blink ensures votes dict exists
            app_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes'. ID: {blink_data.get('id', 'N/A')}. Returning 0.0 interest.")
            return 0.0

        current_votes = blink_data['votes'] # Already converted by get_blink if needed
        positive_votes = current_votes.get('positive', 0)
        negative_votes = current_votes.get('negative', 0)

        total_votes = positive_votes + negative_votes
        net_vote_difference = positive_votes - negative_votes

        if total_votes == 0:
            interest = 0.0
        else:
            interest = (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0

        app_logger.debug(f"calculate_interest_percentage for ID {blink_data.get('id', 'N/A')}: P={positive_votes}, N={negative_votes}, Total={total_votes}, NetDiff={net_vote_difference}, C={confidence_factor_c} -> Interest={interest:.2f}%")
        return interest

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
                blink = self.get_blink(blink_id_from_filename)
                if not blink:
                    app_logger.error(f"Failed to load or process blink from file {filename}. Skipping.")
                    continue

                # Ensure ID is consistent with filename if missing in content
                blink.setdefault('id', blink_id_from_filename)

                # Ensure votes structure is initialized (get_blink should handle conversion and existence)
                current_votes = blink.setdefault('votes', {})
                current_votes.setdefault('positive', 0)
                current_votes.setdefault('negative', 0)

                if 'publishedAt' not in blink or not blink['publishedAt']:
                    app_logger.warning(f"Missing 'publishedAt' for blink_id='{blink.get('id')}' in file {filename}. Using fallback date.")
                    blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                blink['interestPercentage'] = self.calculate_interest_percentage(blink)
                if user_id:
                    blink['currentUserVoteStatus'] = self._get_user_vote_status(blink, user_id)
                else:
                    blink['currentUserVoteStatus'] = None
                blinks_processed.append(blink)
                app_logger.debug(f"Processed blink_id='{blink.get('id')}': Interest={blink['interestPercentage']:.2f}%, UserVote='{blink['currentUserVoteStatus']}', Votes(P/N): {current_votes['positive']}/{current_votes['negative']}")
            except Exception as e:
                app_logger.error(f"Error processing blink file {filename} in get_all_blinks loop: {e}", exc_info=True)

        app_logger.info(f"Successfully processed {len(blinks_processed)} blinks. Now sorting.")

        def compare_blinks(b1, b2):
            # Intensive logging for b1 and b2 details
            b1_id = b1.get('id', 'N/A')
            b2_id = b2.get('id', 'N/A')
            app_logger.debug(f"compare_blinks: Comparing b1 (ID: {b1_id}, Interest: {b1['interestPercentage']:.2f}%, Votes P/N: {b1['votes'].get('positive',0)}/{b1['votes'].get('negative',0)}, Date: {b1['publishedAt']}) "
                             f"with b2 (ID: {b2_id}, Interest: {b2['interestPercentage']:.2f}%, Votes P/N: {b2['votes'].get('positive',0)}/{b2['votes'].get('negative',0)}, Date: {b2['publishedAt']})")

            # 1. Primary sort: interestPercentage (DESC)
            if b1['interestPercentage'] > b2['interestPercentage']:
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b1 interest > b2 interest. Result: -1 (b1 first)")
                return -1
            if b1['interestPercentage'] < b2['interestPercentage']:
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b1 interest < b2 interest. Result: 1 (b2 first)")
                return 1

            # At this point, interestPercentage is tied.
            app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): interestPercentage is TIED ({b1['interestPercentage']:.2f}%). Applying tie-breaking rules.")

            b1_positive = b1['votes'].get('positive', 0)
            b1_negative = b1['votes'].get('negative', 0)
            b2_positive = b2['votes'].get('positive', 0)
            b2_negative = b2['votes'].get('negative', 0)

            try:
                b1_date = datetime.fromisoformat(b1['publishedAt'].replace('Z', '+00:00'))
            except ValueError:
                app_logger.warning(f"compare_blinks ({b1_id}): ValueError parsing b1 publishedAt '{b1['publishedAt']}'. Using fallback date.")
                b1_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
            try:
                b2_date = datetime.fromisoformat(b2['publishedAt'].replace('Z', '+00:00'))
            except ValueError:
                app_logger.warning(f"compare_blinks ({b2_id}): ValueError parsing b2 publishedAt '{b2['publishedAt']}'. Using fallback date.")
                b2_date = datetime(1970, 1, 1, tzinfo=timezone.utc)

            # Rule A: interestPercentage == 0.0 AND positiveVotes == 0 AND negativeVotes == 0 for both
            # This implies interestPercentage is 0.0 for both as we are in the tie section.
            is_b1_rule_a_criteria = b1['interestPercentage'] == 0.0 and b1_positive == 0 and b1_negative == 0
            is_b2_rule_a_criteria = b2['interestPercentage'] == 0.0 and b2_positive == 0 and b2_negative == 0

            if is_b1_rule_a_criteria and is_b2_rule_a_criteria:
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): Both match Rule A criteria (0 interest, 0 positive, 0 negative). Sorting by publishedAt DESC.")
                if b1_date > b2_date: return -1 # b1 is newer, comes first
                if b1_date < b2_date: return 1  # b2 is newer, comes first
                return 0 # Should be rare with full timestamps

            # Handling cases where one is Rule A and the other isn't (and interest is tied at 0.0)
            # If b1 is Rule A and b2 is not (but b2 also has 0.0% interest, e.g. from 0 pos / X neg, or N pos / M neg that balances to 0.0%),
            # Rule A item (no votes) should come after.
            if is_b1_rule_a_criteria and not is_b2_rule_a_criteria: # b1 is 0/0/0, b2 has some votes but still 0% interest (e.g. 0 pos / X neg, or balanced votes)
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b1 matches Rule A (0/0/0), b2 does not but has same 0% interest. b1 comes after. Result: 1")
                return 1
            if not is_b1_rule_a_criteria and is_b2_rule_a_criteria: # b2 is 0/0/0, b1 has some votes but still 0% interest
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b2 matches Rule A (0/0/0), b1 does not but has same 0% interest. b2 comes after. Result: -1")
                return -1

            # Rule B: Tied interest (and not Rule A), AND positiveVotes == 0 AND negativeVotes > 0 for both
            is_b1_rule_b_criteria = b1_positive == 0 and b1_negative > 0
            is_b2_rule_b_criteria = b2_positive == 0 and b2_negative > 0

            if is_b1_rule_b_criteria and is_b2_rule_b_criteria:
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): Both match Rule B criteria (0 positive, >0 negative). Sorting by negativeVotes ASC.")
                if b1_negative < b2_negative: return -1 # b1 has fewer negative votes, comes first
                if b1_negative > b2_negative: return 1  # b2 has fewer negative votes, comes first
                # If negative votes are also tied, fall through to date sort
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): Rule B, negative votes also tied ({b1_negative}). Fall to date sort.")


            # Handling cases where one is Rule B and the other isn't (and interest is tied, and neither is Rule A)
            # A non-Rule B item (e.g. has positive votes, or 0 neg votes but not Rule A) ranks higher than a Rule B item if interest is tied.
            if is_b1_rule_b_criteria and not is_b2_rule_b_criteria:
                # b1 is (0 pos, >0 neg). b2 is not (could be >0 pos, or 0 pos/0 neg which means Rule A - handled above).
                # If b2 has positive votes, it's not Rule B. If interests are tied (e.g. at 0%), a (0, >0) item should come after an item with positive votes or 0/0 votes.
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b1 is Rule B, b2 is not. b1 comes after. Result: 1")
                return 1
            if not is_b1_rule_b_criteria and is_b2_rule_b_criteria:
                # b2 is (0 pos, >0 neg). b1 is not.
                app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): b2 is Rule B, b1 is not. b2 comes after. Result: -1")
                return -1

            # Default tie-breaker: publishedAt (DESC) for any other ties not covered by A or B
            app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): Default tie-breaker: sorting by publishedAt DESC.")
            if b1_date > b2_date: return -1
            if b1_date < b2_date: return 1

            app_logger.debug(f"compare_blinks ({b1_id} vs {b2_id}): All criteria tied. Result: 0")
            return 0

        sorted_blinks = sorted(blinks_processed, key=cmp_to_key(compare_blinks))
        app_logger.info(f"Sorting complete. Returning {len(sorted_blinks)} blinks.")
        if len(sorted_blinks) > 0:
            app_logger.debug(f"Top sorted blink (Destacada): ID='{sorted_blinks[0].get('id')}', Votes(P/N): {sorted_blinks[0]['votes']['positive']}/{sorted_blinks[0]['votes']['negative']}, Interest={sorted_blinks[0].get('interestPercentage'):.2f}%")
            app_logger.debug(f"Last sorted blink (Última): ID='{sorted_blinks[-1].get('id')}', Votes(P/N): {sorted_blinks[-1]['votes']['positive']}/{sorted_blinks[-1]['votes']['negative']}, Interest={sorted_blinks[-1].get('interestPercentage'):.2f}%")
        return sorted_blinks
