import os
import json
from datetime import datetime, timezone
from functools import cmp_to_key

# Attempt to import the logger.
# If models.news is at root, and logger_config is in news-blink-backend/src/
# This import might be tricky depending on how PYTHONPATH is set up or how the app is run.
# A common pattern is for the app instance (Flask) to create and pass the logger,
# or for the logger to be a globally accessible singleton configured at app startup.
# For now, let's try a direct import path assuming PYTHONPATH allows it.
# If this fails, passing the logger to the News class instance would be an alternative.
try:
    from news_blink_backend.src.logger_config import app_logger
except ImportError:
    # Fallback logger if the main one can't be imported (e.g., running model standalone)
    import logging
    app_logger = logging.getLogger(__name__) # Use current module's name
    app_logger.setLevel(logging.DEBUG)
    if not app_logger.hasHandlers(): # Add a basic handler if none configured
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        app_logger.addHandler(ch)
    app_logger.warning("Failed to import app_logger from news_blink_backend.src.logger_config. Using fallback basic logger for models.news.")


class News:
    """Clase para gestionar el almacenamiento y la recuperación de datos de noticias."""

    def __init__(self, data_dir):
        """Inicializa el modelo de noticias, creando los directorios necesarios."""
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
        """Guarda las noticias crudas en un archivo JSON con timestamp."""
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
        """Guarda un único BLINK en un archivo JSON."""
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.debug(f"Attempting to save blink_id='{blink_id}' to {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blink_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved blink_id='{blink_id}' to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving blink_id='{blink_id}' to {filepath}: {e}", exc_info=True)
            raise # Re-raise after logging if callers expect to handle it

    def get_blink(self, blink_id):
        """Obtiene un BLINK específico por su ID."""
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        app_logger.debug(f"Attempting to get blink_id='{blink_id}' from {filepath}")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                app_logger.debug(f"Successfully loaded blink_id='{blink_id}' from {filepath}")
                return data
            except Exception as e:
                app_logger.error(f"Error reading blink_id='{blink_id}' from {filepath}: {e}", exc_info=True)
        else:
            app_logger.warning(f"Blink file not found for blink_id='{blink_id}' at {filepath}")
        return None

    def save_article(self, article_id, article_data):
        """Guarda un artículo completo en un archivo JSON."""
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        app_logger.debug(f"Attempting to save article_id='{article_id}' to {filepath}")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
            app_logger.info(f"Saved article_id='{article_id}' to {filepath}")
        except Exception as e:
            app_logger.error(f"Error saving article_id='{article_id}' to {filepath}: {e}", exc_info=True)
            raise # Re-raise

    def get_article(self, article_id):
        """Obtiene un artículo específico por su ID."""
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        app_logger.debug(f"Attempting to get article_id='{article_id}' from {filepath}")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                app_logger.debug(f"Successfully loaded article_id='{article_id}' from {filepath}")
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

        blink.setdefault('votes', {'positive': 0, 'negative': 0})
        blink['votes'].setdefault('positive', 0)
        blink['votes'].setdefault('negative', 0)
        blink.setdefault('user_votes', {})
        if 'publishedAt' not in blink or not blink['publishedAt']:
            app_logger.warning(f"process_vote: Missing 'publishedAt' for article_id='{article_id}'. Setting to current UTC time.")
            blink['publishedAt'] = datetime.now(timezone.utc).isoformat()

        previous_user_vote = blink['user_votes'].get(user_id)
        app_logger.debug(f"process_vote: article_id='{article_id}', user_id='{user_id}'. Previous vote: '{previous_user_vote}', New vote: '{new_vote_type}'. Current total votes: P={blink['votes']['positive']}, N={blink['votes']['negative']}")

        original_positive = blink['votes']['positive']
        original_negative = blink['votes']['negative']

        if previous_user_vote == new_vote_type:
            app_logger.info(f"process_vote: User '{user_id}' re-voted '{new_vote_type}' for article_id='{article_id}'. No change in vote counts.")
            pass
        else:
            # Adjust counts based on previous vote
            if previous_user_vote == 'positive':
                blink['votes']['positive'] = max(0, blink['votes'].get('positive', 0) - 1)
            elif previous_user_vote == 'negative':
                blink['votes']['negative'] = max(0, blink['votes'].get('negative', 0) - 1)

            # Add new vote
            if new_vote_type == 'positive':
                blink['votes']['positive'] = blink['votes'].get('positive', 0) + 1
            elif new_vote_type == 'negative':
                blink['votes']['negative'] = blink['votes'].get('negative', 0) + 1

            blink['user_votes'][user_id] = new_vote_type
            app_logger.info(f"process_vote: Vote changed for article_id='{article_id}', user_id='{user_id}'. From '{previous_user_vote}' to '{new_vote_type}'. "
                            f"Vote counts changed from P={original_positive}, N={original_negative} to P={blink['votes']['positive']}, N={blink['votes']['negative']}.")

        try:
            self.save_blink(article_id, blink) # save_blink already logs success/failure
        except Exception: # save_blink re-raises on error
            app_logger.error(f"process_vote: Critical failure saving blink_id='{article_id}' after vote. Vote processing aborted.")
            return None # Indicate failure if save_blink failed

        try:
            article_data_to_sync = self.get_article(article_id)
            if article_data_to_sync:
                app_logger.debug(f"process_vote: Syncing votes for full article_id='{article_id}'.")
                article_data_to_sync['votes'] = blink['votes']
                article_data_to_sync['user_votes'] = blink['user_votes']
                self.save_article(article_id, article_data_to_sync) # save_article already logs
        except Exception as e:
            # This error is less critical if blink save succeeded.
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
        if not isinstance(blink_data, dict) or 'votes' not in blink_data:
            app_logger.warning(f"calculate_interest_percentage: Invalid blink_data or missing 'votes'. ID: {blink_data.get('id', 'N/A')}. Returning 0.0 interest.")
            return 0.0

        positive_votes = blink_data['votes'].get('positive', 0)
        negative_votes = blink_data['votes'].get('negative', 0)
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
            filepath = os.path.join(self.blinks_dir, filename)
            app_logger.debug(f"Processing blink file: {filename}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    blink = json.load(f)

                blink_id = blink.get('id', filename.replace('.json', ''))
                blink.setdefault('id', blink_id) # Ensure ID is in the blink data

                blink.setdefault('votes', {'positive': 0, 'negative': 0})
                blink['votes'].setdefault('positive', 0)
                blink['votes'].setdefault('negative', 0)

                if 'publishedAt' not in blink or not blink['publishedAt']:
                    app_logger.warning(f"Missing 'publishedAt' for blink_id='{blink_id}' in file {filename}. Using fallback date.")
                    blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                blink['interestPercentage'] = self.calculate_interest_percentage(blink)
                if user_id:
                    blink['currentUserVoteStatus'] = self._get_user_vote_status(blink, user_id)
                else:
                    blink['currentUserVoteStatus'] = None
                blinks_processed.append(blink)
                app_logger.debug(f"Processed blink_id='{blink_id}': Interest={blink['interestPercentage']:.2f}%, UserVote='{blink['currentUserVoteStatus']}'")
            except Exception as e:
                app_logger.error(f"Error reading or processing blink file {filename}: {e}", exc_info=True)

        app_logger.info(f"Successfully processed {len(blinks_processed)} blinks. Now sorting.")

        def compare_blinks(b1, b2):
            # This comparison function does not need extensive logging itself,
            # as the inputs (interestPercentage, votes, publishedAt) are already logged per blink.
            if b1['interestPercentage'] > b2['interestPercentage']: return -1
            if b1['interestPercentage'] < b2['interestPercentage']: return 1

            b1_positive = b1['votes'].get('positive', 0)
            b1_negative = b1['votes'].get('negative', 0)
            b2_positive = b2['votes'].get('positive', 0)
            b2_negative = b2['votes'].get('negative', 0)

            try: b1_date = datetime.fromisoformat(b1['publishedAt'].replace('Z', '+00:00'))
            except ValueError: b1_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
            try: b2_date = datetime.fromisoformat(b2['publishedAt'].replace('Z', '+00:00'))
            except ValueError: b2_date = datetime(1970, 1, 1, tzinfo=timezone.utc)

            is_b1_no_votes = b1['interestPercentage'] == 0.0 and b1_positive == 0 and b1_negative == 0
            is_b2_no_votes = b2['interestPercentage'] == 0.0 and b2_positive == 0 and b2_negative == 0
            if is_b1_no_votes and is_b2_no_votes: return (b2_date > b1_date) - (b2_date < b1_date)

            is_b1_rule_b = b1_positive == 0 and b1_negative > 0
            is_b2_rule_b = b2_positive == 0 and b2_negative > 0
            if is_b1_rule_b and is_b2_rule_b: return (b1_negative > b2_negative) - (b1_negative < b2_negative)
            if is_b1_rule_b: return 1
            if is_b2_rule_b: return -1

            return (b2_date > b1_date) - (b2_date < b1_date)

        sorted_blinks = sorted(blinks_processed, key=cmp_to_key(compare_blinks))
        app_logger.info(f"Sorting complete. Returning {len(sorted_blinks)} blinks.")
        if len(sorted_blinks) > 0:
            app_logger.debug(f"Top sorted blink (Destacada): ID='{sorted_blinks[0].get('id')}', Interest={sorted_blinks[0].get('interestPercentage'):.2f}%")
            app_logger.debug(f"Last sorted blink (Última): ID='{sorted_blinks[-1].get('id')}', Interest={sorted_blinks[-1].get('interestPercentage'):.2f}%")
        return sorted_blinks
