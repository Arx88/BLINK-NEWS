import os
import json
from datetime import datetime

class News:
    """Clase para gestionar el almacenamiento y la recuperación de datos de noticias."""

    def __init__(self, data_dir):
        """Inicializa el modelo de noticias, creando los directorios necesarios."""
        self.data_dir = data_dir
        self.raw_news_dir = os.path.join(data_dir, 'raw_news')
        self.blinks_dir = os.path.join(data_dir, 'blinks')
        self.articles_dir = os.path.join(data_dir, 'articles')
        
        # Crear directorios si no existen
        os.makedirs(self.raw_news_dir, exist_ok=True)
        os.makedirs(self.blinks_dir, exist_ok=True)
        os.makedirs(self.articles_dir, exist_ok=True)

    def save_raw_news(self, news_items):
        """Guarda las noticias crudas en un archivo JSON con timestamp."""
        filename = f"raw_news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = os.path.join(self.raw_news_dir, filename)
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, ensure_ascii=False, indent=2)
            print(f"Guardadas {len(news_items)} noticias crudas en {filepath}")
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

    def get_all_blinks(self):
        """Obtiene todos los BLINKs guardados."""
        blinks = []
        if not os.path.exists(self.blinks_dir):
            return blinks
            
        for filename in os.listdir(self.blinks_dir):
            if filename.endswith('.json'):
                filepath = os.path.join(self.blinks_dir, filename)
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        blinks.append(json.load(f))
                except Exception as e:
                    print(f"Error al leer el archivo de BLINK {filename}: {e}")
        return blinks

    def save_article(self, article_id, article_data):
        """Guarda un artículo completo en un archivo JSON."""
        filepath = os.path.join(self.articles_dir, f"{article_id}.json")
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error al guardar el artículo {article_id}: {e}")
            raise
            raise

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

    def update_vote(self, article_id, vote_type):
        """Actualiza el contador de votos para un BLINK/artículo."""
        blink = self.get_blink(article_id)
        if not blink:
            print(f"Error en update_vote: No se encontró el blink con ID {article_id} al intentar votar.") # Added log
            return False

        if 'votes' not in blink:
            blink['votes'] = {'likes': 0, 'dislikes': 0}

        if vote_type == 'like':
            blink['votes']['likes'] = blink['votes'].get('likes', 0) + 1
        elif vote_type == 'dislike':
            blink['votes']['dislikes'] = blink['votes'].get('dislikes', 0) + 1

        try:
            self.save_blink(article_id, blink)
        except Exception as e:
            print(f"Error crítico en update_vote al intentar guardar BLINK {article_id} después de actualizar votos: {e}")
            return False # Indicates failure to the caller in routes/api.py

        # Try to update the corresponding article file as well
        try:
            article = self.get_article(article_id) # This part should be safe, but good to have in try if logic grows
            if article:
                article['votes'] = blink['votes'] # Sync votes
                self.save_article(article_id, article)
        except Exception as e:
            # This error is less critical than blink save, but still important to log
            # and potentially signal as a partial failure if desired.
            # For now, if blink save succeeded, we might still consider the vote operation "successful enough"
            # for the primary data, but log this failure clearly.
            print(f"Error crítico en update_vote al intentar guardar ARTÍCULO {article_id} después de actualizar votos: {e}")
            # Depending on policy, you might return False here too, or just log.
            # Let's make it strict: if article save fails, the overall operation is a failure.
            return False

        return True
        if not blink:
            return False

        if 'votes' not in blink:
            blink['votes'] = {'likes': 0, 'dislikes': 0}

        if vote_type == 'like':
            blink['votes']['likes'] = blink['votes'].get('likes', 0) + 1
        elif vote_type == 'dislike':
            blink['votes']['dislikes'] = blink['votes'].get('dislikes', 0) + 1
        
        # Guardar los cambios en el archivo del BLINK y del artículo si existe
        self.save_blink(article_id, blink)
        
        article = self.get_article(article_id)
        if article:
            article['votes'] = blink['votes']
            self.save_article(article_id, article)
            
        return True