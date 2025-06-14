import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from nltk.tokenize import word_tokenize
import hashlib
import os
import json
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import re
# from models.image_generator import ImageGenerator # <-- LÍNEA COMENTADA
import ollama

ALLOWED_CATEGORIES = ["tecnología", "deportes", "entretenimiento", "política", "economía", "salud", "ciencia", "mundo", "cultura", "general"]

class BlinkGenerator:
    """Clase para generar resúmenes en formato BLINK a partir de noticias"""

    def __init__(self):
        """Inicializa el generador de BLINKS"""
        # Descargar recursos de NLTK necesarios
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')

        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')

        # Inicializar el generador de imágenes
        # self.image_generator = ImageGenerator() # <-- LÍNEA COMENTADA

        # Leer la URL de Ollama desde la variable de entorno
        ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
        self.ollama_client = ollama.Client(host=ollama_base_url)
        self.ollama_model = 'qwen3:32b' # Modelo por defecto, se puede configurar

    def determine_category_with_ai(self, text_content, title):
        if not text_content and not title:
            return "general" # Not enough info to determine category

        # Combine title and content for better context, prioritizing content
        input_text = text_content if text_content else ""
        if title:
            input_text = title + "\n\n" + input_text

        # Limit input text length to avoid overly long prompts (e.g., first 1000 chars)
        input_text = input_text[:1000]

        categories_str = ", ".join(ALLOWED_CATEGORIES)
        prompt = f"""
Analiza el siguiente texto de una noticia y clasifícalo en UNA de las siguientes categorías: {categories_str}.

Título: {title}
Texto:
{input_text}

Responde ÚNICAMENTE con el nombre de la categoría que mejor se ajuste al texto. No añadas ninguna explicación, puntuación o frase adicional.
Categoría:"""

        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': 0.2} # Low temperature for more deterministic category output
            )

            raw_category = response['message']['content'].strip().lower()

            # Clean the response: sometimes the model might add extra text or quotes
            # We want to find the best match from ALLOWED_CATEGORIES
            best_match_category = "general" # Default

            # Iterate through allowed categories and check if the raw_category contains any of them.
            # This handles cases where the model might output "Categoría: deportes" instead of just "deportes".
            for cat in ALLOWED_CATEGORIES:
                if cat in raw_category:
                    best_match_category = cat
                    break # Found a direct match

            # If no substring match, check if the raw_category itself is a valid one.
            # This handles cases where the model perfectly outputs just the category name.
            if best_match_category == "general" and raw_category in ALLOWED_CATEGORIES:
                best_match_category = raw_category

            print(f"DEBUG: Determined category: {best_match_category} (raw: {raw_category}) for title: {title}")
            return best_match_category

        except ollama.ResponseError as e:
            print(f"Error communicating with Ollama for category determination: {e.error}")
            return "general" # Fallback category
        except Exception as e:
            print(f"Unexpected error in determine_category_with_ai: {e}")
            return "general" # Fallback category

    def verify_category_with_ai(self, text_content, title, proposed_category):
        if not text_content and not title:
            # Not enough info to verify, assume previous category determination was weak
            return False, proposed_category

        # Combine title and content for better context, prioritizing content
        input_text = text_content if text_content else ""
        if title:
            input_text = title + "\n\n" + input_text

        # Limit input text length (e.g., first 1000 chars)
        input_text = input_text[:1000]

        prompt = f"""
Se ha clasificado una noticia con el título "{title}" y el siguiente texto como perteneciente a la categoría "{proposed_category}".

Texto de la noticia:
{input_text}

¿Consideras que esta clasificación en la categoría "{proposed_category}" es correcta? Responde únicamente con "sí" o "no".
Respuesta:"""

        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': 0.1} # Very low temperature for a simple yes/no
            )

            verification_response = response['message']['content'].strip().lower()
            print(f"DEBUG: Verification response for category '{proposed_category}' for title '{title}': {verification_response}")

            if "sí" in verification_response or "si" in verification_response: # Accept with or without accent
                return True, proposed_category
            elif "no" in verification_response:
                return False, proposed_category # Verification failed
            else:
                # Unclear response, treat as verification failed to be safe
                print(f"DEBUG: Unclear verification response. Defaulting to not verified.")
                return False, proposed_category

        except ollama.ResponseError as e:
            print(f"Error communicating with Ollama for category verification: {e.error}")
            # If verification fails due to error, assume not verified
            return False, proposed_category
        except Exception as e:
            print(f"Unexpected error in verify_category_with_ai: {e}")
            # If verification fails due to error, assume not verified
            return False, proposed_category

    def generate_blink_from_news_group(self, news_group):
        """Genera un resumen en formato BLINK a partir de un grupo de noticias similares"""
        # Usar el título más representativo del grupo
        title = self.select_best_title(news_group)

        # Combinar contenido de todas las noticias
        combined_content = ""
        sources = []
        urls = []

        for item in news_group:
            if 'url' in item:
                urls.append(item['url'])
                sources.append(item['source'])

        # Obtener contenido completo de los artículos
        article_contents = []
        image_url = None

        for url in urls[:3]:  # Limitar a 3 URLs para evitar sobrecarga
            try:
                content_data = self.get_article_content(url)
                if content_data['content']:
                    article_contents.append(content_data['content'])
                    combined_content += " " + content_data['content']

                # Usar la primera imagen encontrada
                if not image_url and content_data['image_url']:
                    image_url = content_data['image_url']

            except Exception as e:
                print(f"Error al procesar URL {url}: {e}")

        # Si no se encontró contenido, usar los resúmenes disponibles
        if not combined_content:
            for item in news_group:
                if 'summary' in item and item['summary']:
                    combined_content += " " + item['summary']

        # Si no se encontró ninguna imagen, generar una automáticamente
        # if not image_url: # <-- INICIO DE BLOQUE COMENTADO
        #     image_url = self.image_generator.generate_image_for_blink(title, combined_content) # <-- LÍNEA COMENTADA

        # Generar puntos clave usando Ollama
        points = self.generate_ollama_summary(combined_content, title)

        # Generar un ID único para el BLINK
        blink_id = hashlib.md5(title.encode()).hexdigest()

        # Determine and verify category
        determined_category_name = self.determine_category_with_ai(combined_content, title)
        is_verified, final_category_name = self.verify_category_with_ai(combined_content, title, determined_category_name)

        if not is_verified:
            final_category_name = "general" # Fallback if verification fails

        # Crear el objeto BLINK
        blink = {
            'id': blink_id,
            'title': title,
            'points': points,
            'image': image_url,
            'sources': list(set(sources)),
            'urls': urls,
            'timestamp': datetime.now().isoformat(),
            'content': combined_content[:15000],
            'categories': [final_category_name],
            'votes': {'likes': 0, 'dislikes': 0}
        }

        return blink

    def select_best_title(self, news_group):
        """Selecciona el mejor título del grupo de noticias"""
        if len(news_group) == 1:
            return news_group[0]['title']

        best_title = news_group[0]['title']
        best_score = 0

        for item in news_group:
            title = item['title']
            score = 0
            length = len(title)
            if 40 <= length <= 80:
                score += 3
            elif 30 <= length <= 100:
                score += 2
            elif 20 <= length <= 120:
                score += 1
            
            important_words = ['inteligencia artificial', 'ia', 'ai', 'tecnología', 'innovación', 'nuevo', 'lanza', 'anuncia']
            for word in important_words:
                if word.lower() in title.lower():
                    score += 2

            punct_count = sum(1 for char in title if char in '!?.:;')
            if punct_count <= 2:
                score += 1
            
            if score > best_score:
                best_score = score
                best_title = title
        
        return best_title

    def get_article_content(self, url):
        """Obtiene el contenido completo de un artículo desde su URL"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside', 'form']):
                element.decompose()

            content = ""
            
            content_selectors = [
                'article',
                'main',
                'div[class*="content"]',
                'div[class*="article"]',
                'div[class*="post"]',
                'div[class*="story"]',
                'div[id*="content"]'
            ]
            
            article_element = None
            for selector in content_selectors:
                article_element = soup.select_one(selector)
                if article_element:
                    break
            
            if article_element:
                paragraphs = article_element.find_all('p')
                content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 30])
            
            image_url = None
            
            meta_tags = [
                soup.find('meta', property='og:image'),
                soup.find('meta', attrs={'name': 'twitter:image'}),
                soup.find('meta', attrs={'property': 'twitter:image'})
            ]
            
            for tag in meta_tags:
                if tag and tag.get('content'):
                    image_url = tag.get('content')
                    break

            if not image_url and article_element:
                img_tags = article_element.find_all('img')
                for img in img_tags:
                    src = img.get('src') or img.get('data-src')
                    if src and (img.get('width') is None or int(img.get('width', 0)) >= 300):
                        if not src.startswith(('http://', 'https://')):
                            base_url = '/'.join(url.split('/')[:3])
                            src = base_url + src.lstrip('/')
                        image_url = src
                        break
            
            return {
                'content': content,
                'image_url': image_url
            }
        except Exception as e:
            print(f"Error al obtener contenido del artículo {url}: {e}")
            return {
                'content': "",
                'image_url': None
            }
    
    def generate_ollama_summary(self, text, title="", num_points=5):
        """Genera un resumen de 5 puntos clave usando Ollama."""
        if not text:
            return self.generate_fallback_points(title, num_points)

        prompt = f"""A partir del siguiente texto de una noticia con el título "{title}", extrae exactamente {num_points} puntos clave.

  Reglas:
  - Cada punto debe ser una oración concisa y clara.
  - No incluyas frases introductorias, explicaciones o numeración.
  - Responde únicamente con los {num_points} puntos, cada uno en una nueva línea. NO INCLUYAS NINGÚN OTRO TEXTO, RAZONAMIENTO O CONVERSACIÓN. SOLO EMITE LA LISTA DE PUNTOS.

  Texto:
  {text}
  """

        try:
            response = self.ollama_client.chat(
                model=self.ollama_model,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': 0.3}
            )
            summary_content = response['message']['content']

            all_lines = summary_content.strip().split('\n')
            extracted_points = []
            for line in reversed(all_lines):
                cleaned_line = re.sub(r'^\s*[\*\-•\d\.]+\s*', '', line).strip()
                if cleaned_line:
                    extracted_points.insert(0, cleaned_line)
                if len(extracted_points) == num_points:
                    break

            points = extracted_points

            if len(points) < num_points:
                missing_points = num_points - len(points)
                fallback_points = self.generate_fallback_points(title, missing_points)
                points.extend(fallback_points)

            return points

        except ollama.ResponseError as e:
            print(f"Error al comunicarse con Ollama: {e.error}")
            return self.generate_fallback_points(title, num_points)
        except Exception as e:
            print(f"Error inesperado al generar resumen con Ollama: {e}")
            return self.generate_fallback_points(title, num_points)

    def generate_fallback_points(self, title, num_points):
        """Genera puntos de respaldo cuando no hay contenido o falla Ollama"""
        if not title:
            return ["Información no disponible en este momento."] * num_points
        
        points = [
            f"Noticia relacionada con: {title}",
            "Múltiples fuentes confirman esta información.",
            "Se esperan más detalles en las próximas horas.",
            "La noticia ha generado interés en la comunidad tecnológica.",
            "Consulte las fuentes originales para más información.",
            "Manténgase actualizado para futuras actualizaciones."
        ]
        
        return points[:num_points]