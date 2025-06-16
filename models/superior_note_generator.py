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

class SuperiorNoteGenerator:
    """Clase para generar notas superiores a partir de múltiples fuentes sobre el mismo tema"""

    def __init__(self):
        """Inicializa el generador de notas superiores"""
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
        self.ollama_model = 'qwen3:32b'  # Modelo por defecto

    def generate_superior_note(self, articles_group, topic):
        """
        Genera una nota superior a partir de múltiples artículos sobre el mismo tema
        """
        print(f"Generando nota superior para el tema: {topic}")

        # Obtener contenido completo de todos los artículos
        all_contents = []
        sources = []
        urls = []

        for article in articles_group:
            try:
                # Obtener contenido completo del artículo
                content_data = self._get_article_content(article['url'])
                if content_data['content']:
                    all_contents.append({
                        'source': article['source'],
                        'title': article['title'],
                        'content': content_data['content'],
                        'url': article['url']
                    })
                    sources.append(article['source'])
                    urls.append(article['url'])
                else:
                    # Si no se puede obtener contenido, usar el resumen
                    all_contents.append({
                        'source': article['source'],
                        'title': article['title'],
                        'content': article.get('summary', ''),
                        'url': article['url']
                    })
                    sources.append(article['source'])
                    urls.append(article['url'])
            except Exception as e:
                print(f"Error procesando artículo de {article['source']}: {e}")
                continue

        if not all_contents:
            raise ValueError("No se pudo obtener contenido de ningún artículo")

        # Generar título principal
        main_title = self._generate_main_title(all_contents, topic)

        # Generar nota superior usando OLLAMA
        superior_note_content = self._generate_comprehensive_note(all_contents, topic)

        # Generar ultra resumen (5 bullets)
        ultra_summary = self._generate_ultra_summary(superior_note_content, topic)

        # Generar imagen para la nota
        # image_url = self.image_generator.generate_image_for_blink(main_title, superior_note_content[:500]) # <-- LÍNEA COMENTADA
        image_url = None # <-- LÍNEA AÑADIDA para que la variable exista

        # Crear ID único
        note_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()

        # Crear objeto de nota superior
        superior_note = {
            'id': note_id,
            'topic': topic,
            'title': main_title,
            'full_content': superior_note_content,
            'ultra_summary': ultra_summary,
            'sources': list(set(sources)),
            'urls': urls,
            'articles_count': len(all_contents),
            'timestamp': datetime.now().isoformat(),
            'image': image_url,
            'original_articles': all_contents
        }

        # Guardar la nota
        self._save_superior_note(superior_note)

        return superior_note

    def _get_article_content(self, url):
        """Obtiene el contenido completo de un artículo"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Remover elementos no deseados
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'advertisement']):
                element.decompose()

            # Buscar el contenido principal del artículo
            content_selectors = [
                'article',
                '.article-content',
                '.post-content',
                '.entry-content',
                '.content',
                'main',
                '.story-body',
                '.article-body'
            ]

            content = ""
            for selector in content_selectors:
                content_elem = soup.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(separator=' ', strip=True)
                    break

            if not content:
                content = soup.get_text(separator=' ', strip=True)

            content = re.sub(r'\s+', ' ', content)
            content = content[:10000]

            image_url = None
            img_selectors = ['meta[property="og:image"]', '.article-image img', 'article img', '.featured-image img']
            for selector in img_selectors:
                img_elem = soup.select_one(selector)
                if img_elem:
                    image_url = img_elem.get('content') or img_elem.get('src')
                    if image_url and image_url.startswith('http'):
                        break

            return {
                'content': content,
                'image_url': image_url
            }

        except Exception as e:
            print(f"Error obteniendo contenido de {url}: {e}")
            return {'content': '', 'image_url': None}

    def _generate_main_title(self, all_contents, topic):
        """Genera un título principal para la nota superior"""
        titles = [content['title'] for content in all_contents]

        best_title = f"Análisis completo: {topic}"

        for title in titles:
            if topic.lower() in title.lower() and len(title) > len(best_title):
                best_title = title

        return best_title

    def _generate_comprehensive_note(self, all_contents, topic):
        """Genera una nota comprehensiva usando OLLAMA"""
        try:
            context = f"Tema principal: {topic}\n\n"
            context += "Artículos de diferentes fuentes:\n\n"

            for i, content in enumerate(all_contents, 1):
                context += f"FUENTE {i} - {content['source']}:\n"
                context += f"Título: {content['title']}\n"
                context += f"Contenido: {content['content'][:2000]}...\n\n"

            prompt = f"""Basándote en los artículos de múltiples fuentes proporcionados sobre el tema "{topic}", crea una NOTA SUPERIOR comprehensiva que:

1. Integre la información de todas las fuentes
2. Presente múltiples puntos de vista y perspectivas
3. Identifique consensos y discrepancias entre las fuentes
4. Proporcione un análisis equilibrado y completo
5. Mantenga un tono periodístico profesional
6. Tenga una extensión de aproximadamente 800-1200 palabras
7. ESTÉ FORMATEADA EN MARKDOWN. Utiliza encabezados (#, ##, ###), listas (con -, * o números), negritas (**texto**), itálicas (*texto*), y párrafos separados por doble salto de línea.

La nota debe estar estructurada con:
- Introducción que presente el tema
- Desarrollo que integre las diferentes perspectivas
- Análisis de los puntos clave
- Conclusión que sintetice la información

Contexto de las fuentes:
{context}

NOTA SUPERIOR (en formato Markdown):"""

            response = self.ollama_client.chat(model=self.ollama_model, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])

            ai_content = response['message']['content']
            # Combine all original content for fallback reference in sanitization
            combined_original_content = "\n\n".join([c['content'] for c in all_contents])
            return self._sanitize_ai_output(ai_content, combined_original_content, topic)

        except Exception as e:
            print(f"Error generando nota con OLLAMA: {e}")
            basic_note_content = self._generate_basic_note(all_contents, topic)
            # Combine all original content for fallback reference in sanitization
            combined_original_content = "\n\n".join([c['content'] for c in all_contents])
            return self._sanitize_ai_output(basic_note_content, combined_original_content, topic)

    def _sanitize_ai_output(self, ai_content: str, original_plain_text: str, title: str) -> str:
        # Normalize line endings
        content = ai_content.replace('\r\n', '\n').replace('\r', '\n')

        # Strip leading/trailing whitespace from the whole content
        content = content.strip()

        # Split into lines, strip each line, and rejoin. This handles individual line whitespace.
        lines = [line.strip() for line in content.split('\n')]
        content = '\n'.join(lines)

        # Attempt to ensure paragraphs are separated by double newlines
        # if no double newlines exist but single newlines do.
        if '\n\n' not in content and '\n' in content:
            # A more careful regex:
            # - Negative lookbehind for a newline (don't act if already \n\n)
            # - A newline
            # - Negative lookahead for a newline, or markdown list/blockquote/header characters
            # This tries to avoid messing up lists or other structures.
            content = re.sub(r'(?<!\n)\n(?![\n*#>\s-])', '\n\n', content)

        # Remove excessive blank lines (more than two consecutive newlines down to two)
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Fallback for severely unformatted text
        # Check if it's still a long block without proper paragraph separation
        # Also, check if it contains at least some typical markdown structuring characters.
        # If not, it's likely the AI just returned a blob of text.
        is_likely_blob = len(content) > 300 and '\n\n' not in content
        has_markdown_chars = any(char in content for char in ['#', '>', '*', '-'])

        if is_likely_blob and not has_markdown_chars:
            print(f"AI output for title '{title}' appears unformatted after sanitization. Using fallback based on original plain text.")
            # Fallback to original plain text, trying to make paragraphs
            fallback_content = original_plain_text.replace('\r\n', '\n').replace('\r', '\n')
            fallback_lines = [line.strip() for line in fallback_content.split('\n') if line.strip()]
            return '\n\n'.join(fallback_lines)

        return content

    def _generate_ultra_summary(self, full_content, topic):
        """Genera un ultra resumen de 5 bullets usando OLLAMA"""
        try:
            prompt = f"""Basándote en la siguiente nota completa sobre "{topic}", crea exactamente 5 bullets que resuman los puntos MÁS IMPORTANTES de manera ultra concisa.

Cada bullet debe:
- Ser una oración completa y clara
- Contener información esencial y relevante
- Ser independiente y comprensible por sí solo
- Tener máximo 25 palabras
- Evitar información redundante

Nota completa:
{full_content}

Responde ÚNICAMENTE con los 5 bullets en este formato:
• [Bullet 1]
• [Bullet 2]
• [Bullet 3]
• [Bullet 4]
• [Bullet 5]"""

            response = self.ollama_client.chat(model=self.ollama_model, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])

            bullets_text = response['message']['content']
            bullets = []

            for line in bullets_text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet = line[1:].strip()
                    if bullet:
                        bullets.append(bullet)

            if len(bullets) < 5:
                bullets.extend([f"Punto adicional {i}" for i in range(len(bullets) + 1, 6)])
            elif len(bullets) > 5:
                bullets = bullets[:5]

            return bullets

        except Exception as e:
            print(f"Error generando ultra resumen con OLLAMA: {e}")
            return [
                f"Información importante sobre {topic}",
                "Múltiples fuentes consultadas",
                "Análisis de diferentes perspectivas",
                "Datos relevantes recopilados",
                "Conclusiones del análisis"
            ]

    def _generate_basic_note(self, all_contents, topic):
        """Genera una nota básica sin OLLAMA (fallback)"""
        note = f"# Análisis completo: {topic}\n\n"
        note += f"Se han analizado {len(all_contents)} fuentes diferentes sobre este tema.\n\n"

        for i, content in enumerate(all_contents, 1):
            note += f"## Perspectiva {i}: {content['source']}\n"
            note += f"**{content['title']}**\n\n"
            note += f"{content['content'][:500]}...\n\n"

        note += "## Conclusión\n"
        note += f"El análisis de múltiples fuentes proporciona una visión comprehensiva sobre {topic}."

        return note

    def _save_superior_note(self, note):
        """Guarda la nota superior en el sistema de archivos"""
        try:
            notes_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'superior_notes')
            os.makedirs(notes_dir, exist_ok=True)

            filename = f"superior_note_{note['id']}.json"
            filepath = os.path.join(notes_dir, filename)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(note, f, ensure_ascii=False, indent=2)

            print(f"Nota superior guardada: {filepath}")

        except Exception as e:
            print(f"Error guardando nota superior: {e}")

    def get_all_superior_notes(self):
        """Obtiene todas las notas superiores guardadas"""
        try:
            notes_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'superior_notes')

            if not os.path.exists(notes_dir):
                return []

            notes = []
            for filename in os.listdir(notes_dir):
                if filename.endswith('.json'):
                    filepath = os.path.join(notes_dir, filename)
                    with open(filepath, 'r', encoding='utf-8') as f:
                        note = json.load(f)
                        notes.append(note)

            notes.sort(key=lambda x: x['timestamp'], reverse=True)
            return notes

        except Exception as e:
            print(f"Error obteniendo notas superiores: {e}")
            return []