import os
import json
from datetime import datetime, timezone # Ensure datetime and timezone are imported
from functools import cmp_to_key # Required for complex sorting

class News:
    """Clase para gestionar el almacenamiento y la recuperación de datos de noticias."""

    def __init__(self, data_dir):
        """Inicializa el modelo de noticias, creando los directorios necesarios."""
        self.data_dir = data_dir
        self.raw_news_dir = os.path.join(data_dir, 'raw_news')
        self.blinks_dir = os.path.join(data_dir, 'blinks')
        self.articles_dir = os.path.join(data_dir, 'articles')

        os.makedirs(self.raw_news_dir, exist_ok=True)
        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

    def save_raw_news(self, news_items):
        """Guarda las noticias crudas en un archivo JSON con timestamp."""
        filename = f"raw_news_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.raw_news_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            # print(f"Guardadas {len(news_items)} noticias crudas en {filepath}")
        except Exception as e:
            print(f"Error al guardar noticias crudas: {e}")

    def save_blink(self, blink_id, blink_data):
        """Guarda un único BLINK en un archivo JSON."""
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(blink_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar el BLINK {blink_id}: {e}")

    def get_blink(self, blink_id):
        """Obtiene un BLINK específico por su ID."""
        filepath = os.path.join(self.blinks_dir, f"{blink_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al leer el BLINK {blink_id}: {e}")
        return None

    def save_article(self, article_id, article_data):
        """Guarda un artículo completo en un archivo JSON."""
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar el artículo {article_id}: {e}")

    def get_article(self, article_id):
        """Obtiene un artículo específico por su ID."""
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        if os.path.exists(filepath):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"Error al leer el artículo {article_id}: {e}")
        return None

    def process_vote(self, article_id, user_id, new_vote_type):
        """
        Procesa un voto para un artículo, actualizando los contadores de votos
        y el registro de votos del usuario.
        `new_vote_type` puede ser 'positive' o 'negative'.
        """
        blink = self.get_blink(article_id)
        if not blink:
            # print(f"Error en process_vote: No se encontró el blink con ID {article_id} al intentar votar.")
            return None

        blink.setdefault('votes', {'positive': 0, 'negative': 0})
        blink['votes'].setdefault('positive', 0)
        blink['votes'].setdefault('negative', 0)

        blink.setdefault('user_votes', {})
        if 'publishedAt' not in blink or not blink['publishedAt']:
            blink['publishedAt'] = datetime.now(timezone.utc).isoformat()

        previous_user_vote = blink['user_votes'].get(user_id)

        if previous_user_vote == new_vote_type:
            pass
        else:
            if previous_user_vote == 'positive':
                blink['votes']['positive'] = max(0, blink['votes'].get('positive', 0) - 1)
            elif previous_user_vote == 'negative':
                blink['votes']['negative'] = max(0, blink['votes'].get('negative', 0) - 1)

            if new_vote_type == 'positive':
                blink['votes']['positive'] = blink['votes'].get('positive', 0) + 1
            elif new_vote_type == 'negative':
                blink['votes']['negative'] = blink['votes'].get('negative', 0) + 1

            blink['user_votes'][user_id] = new_vote_type

        try:
            self.save_blink(article_id, blink)
        except Exception as e:
            # print(f"Error crítico en process_vote al intentar guardar BLINK {article_id} después de actualizar votos: {e}")
            return None

        try:
            article = self.get_article(article_id)
            if article:
                article['votes'] = blink['votes']
                article['user_votes'] = blink['user_votes']
                self.save_article(article_id, article)
        except Exception as e:
            pass # print(f"Advertencia en process_vote: Error al intentar guardar ARTÍCULO {article_id} después de actualizar votos: {e}")

        return blink

    def _get_user_vote_status(self, blink_data, user_id):
        """
        Obtiene el estado de voto de un usuario para un blink específico.
        Retorna 'positive', 'negative', o None.
        """
        if not isinstance(blink_data, dict):
            return None
        return blink_data.get('user_votes', {}).get(user_id)

    def calculate_interest_percentage(self, blink_data, confidence_factor_c=5):
        """Calcula el porcentaje de interés para un blink."""
        if not isinstance(blink_data, dict) or 'votes' not in blink_data:
            return 0.0

        positive_votes = blink_data['votes'].get('positive', 0)
        negative_votes = blink_data['votes'].get('negative', 0)

        total_votes = positive_votes + negative_votes
        net_vote_difference = positive_votes - negative_votes

        if total_votes == 0:
            return 0.0
        else:
            return (net_vote_difference / (total_votes + confidence_factor_c)) * 100.0

    def get_all_blinks(self, user_id=None):
        """Obtiene todos los BLINKs guardados, calculando interés y ordenándolos."""
        blinks_raw = []
        if not os.path.exists(self.blinks_dir):
            return blinks_raw

        for filename in os.listdir(self.blinks_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.blinks_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        blink = json.load(f)
                        # Ensure essential fields for sorting are present
                        blink.setdefault('votes', {'positive': 0, 'negative': 0})
                        blink['votes'].setdefault('positive', 0)
                        blink['votes'].setdefault('negative', 0)
                        if 'publishedAt' not in blink or not blink['publishedAt']:
                            # Fallback for missing publishedAt - older items go last in date sort
                            blink['publishedAt'] = datetime(1970, 1, 1, tzinfo=timezone.utc).isoformat()

                        blink['interestPercentage'] = self.calculate_interest_percentage(blink)
                        if user_id:
                            blink['currentUserVoteStatus'] = self._get_user_vote_status(blink, user_id)
                        else:
                            blink['currentUserVoteStatus'] = None
                        blinks_raw.append(blink)
                except Exception as e:
                    # print(f"Error al leer o procesar el archivo de BLINK {filename}: {e}")
                    pass # Continue with other blinks

        # Sorting logic
        def compare_blinks(b1, b2):
            # 1. Primary: Interest Percentage (DESC)
            if b1['interestPercentage'] > b2['interestPercentage']:
                return -1
            if b1['interestPercentage'] < b2['interestPercentage']:
                return 1

            # At this point, interestPercentage is equal. Apply tie-breaking.
            b1_positive = b1['votes'].get('positive', 0)
            b1_negative = b1['votes'].get('negative', 0)
            b2_positive = b2['votes'].get('positive', 0)
            b2_negative = b2['votes'].get('negative', 0)

            # Try to parse dates safely
            try:
                b1_date = datetime.fromisoformat(b1['publishedAt'].replace('Z', '+00:00'))
            except ValueError: # Fallback for invalid date format
                 b1_date = datetime(1970, 1, 1, tzinfo=timezone.utc)
            try:
                b2_date = datetime.fromisoformat(b2['publishedAt'].replace('Z', '+00:00'))
            except ValueError: # Fallback for invalid date format
                 b2_date = datetime(1970, 1, 1, tzinfo=timezone.utc)


            # Rule A (No Votes: Interest 0%, Positive 0, Negative 0): By publishedAt (DESC)
            is_b1_no_votes = b1['interestPercentage'] == 0.0 and b1_positive == 0 and b1_negative == 0
            is_b2_no_votes = b2['interestPercentage'] == 0.0 and b2_positive == 0 and b2_negative == 0

            if is_b1_no_votes and is_b2_no_votes:
                return (b2_date > b1_date) - (b2_date < b1_date) # DESC date sort

            # Rule B (0 Positive, >0 Negative): By negative_votes (ASC)
            # This rule applies if interest is 0 (could be due to C factor or equal pos/neg votes)
            # and specifically positive votes are 0 and negative > 0.
            is_b1_rule_b = b1_positive == 0 and b1_negative > 0
            is_b2_rule_b = b2_positive == 0 and b2_negative > 0

            if is_b1_rule_b and is_b2_rule_b: # Both qualify for Rule B
                return (b1_negative > b2_negative) - (b1_negative < b2_negative) # ASC negative_votes
            elif is_b1_rule_b: # Only b1 qualifies, b2 doesn't (so b1 might come after if b2 is not rule B)
                return 1 # Put b1 later if b2 is not Rule B and has 0% interest
            elif is_b2_rule_b: # Only b2 qualifies
                return -1 # Put b2 later

            # Default tie-break: publishedAt (DESC) for any other 0% interest ties or general ties
            return (b2_date > b1_date) - (b2_date < b1_date)

        return sorted(blinks_raw, key=cmp_to_key(compare_blinks))
