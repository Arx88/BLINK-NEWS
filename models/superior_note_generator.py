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

        # Cargar configuraciones de IA desde config.json
        self.ai_configs = {}
        try:
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                loaded_configs = json.load(f)
                if 'ai_task_configs' in loaded_configs:
                    self.ai_configs = loaded_configs['ai_task_configs']
                else:
                    print("Advertencia: 'ai_task_configs' no encontrado en config.json")
        except FileNotFoundError:
            print(f"Advertencia: config.json no encontrado en {config_path}")
        except json.JSONDecodeError:
            print(f"Advertencia: Error decodificando config.json en {config_path}")


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

        # Generar título principal
        main_title = self._generate_main_title(all_contents, topic)

        # Generar contenido en bruto de la nota superior
        print(f"Generando contenido en bruto para: {main_title}")
        raw_note_content = self._generate_comprehensive_note(all_contents, topic)

        # Aplicar formato Markdown
        print(f"Aplicando formato Markdown para: {main_title}")
        formatted_note_content = self._format_note_with_markdown(raw_note_content, main_title)

        # Generar ultra resumen (5 bullets)
        print(f"Generando ultra resumen para: {main_title}")
        ultra_summary = self._generate_ultra_summary(formatted_note_content, topic)

        # Generar imagen para la nota
        # image_url = self.image_generator.generate_image_for_blink(main_title, formatted_note_content[:500]) # <-- LÍNEA COMENTADA
        image_url = None # <-- LÍNEA AÑADIDA para que la variable exista

        # Crear ID único
        note_id = hashlib.md5(f"{topic}_{datetime.now().isoformat()}".encode()).hexdigest()

        # Crear objeto de nota superior
        superior_note = {
            'id': note_id,
            'topic': topic,
            'title': main_title,
            'full_content': formatted_note_content,
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

1. Integre la información de todas las fuentes.
2. Presente múltiples puntos de vista y perspectivas.
3. Identifique consensos y discrepancias entre las fuentes.
4. Proporcione un análisis equilibrado y completo.
5. Mantenga un tono periodístico profesional.
6. Tenga una extensión de aproximadamente 800-1200 palabras.

La nota debe estar estructurada con:
- Una introducción clara que presente el tema y su importancia.
- Un desarrollo que integre la información de las diferentes fuentes, analizando los puntos clave, similitudes y diferencias.
- Una conclusión que sintetice la información y ofrezca una perspectiva general.

Contexto de las fuentes:
{context}

NOTA SUPERIOR (solo texto, sin formato Markdown):"""

            response = self.ollama_client.chat(model=self.ollama_model, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            return response['message']['content']

        except Exception as e:
            print(f"Error generando nota con OLLAMA: {e}")
            # En caso de error, devolvemos una versión básica que ya tiene algo de Markdown,
            # pero la idea es que _format_note_with_markdown lo procese si es necesario.
            return self._generate_basic_note(all_contents, topic)

    def _format_note_with_markdown(self, raw_note_content, title):
        """Formatea el contenido de la nota usando Markdown a través de OLLAMA y config.json"""
        try:
            formatter_config = self.ai_configs.get('format_main_content')
            if not formatter_config:
                print("Advertencia: 'format_main_content' no encontrado en la configuración de IA. Devolviendo contenido en bruto.")
                return raw_note_content

            prompt_template = formatter_config.get('prompt_template')
            if not prompt_template:
                print("Advertencia: 'prompt_template' para 'format_main_content' no encontrado. Devolviendo contenido en bruto.")
                return raw_note_content

            model_name = formatter_config.get('model_name', self.ollama_model)
            temperature = formatter_config.get('temperature', 0.6)
            max_chars = formatter_config.get('input_max_chars', 20000) # Max input chars for the formatter

            effective_content = raw_note_content[:max_chars]

            formatted_prompt = prompt_template.format(title=title, effective_plain_text_content=effective_content)

            print(f"Enviando a OLLAMA para formateo Markdown (modelo: {model_name}, temp: {temperature}):\n{formatted_prompt[:300]}...")


            response = self.ollama_client.chat(
                model=model_name,
                messages=[{'role': 'user', 'content': formatted_prompt}],
                options={'temperature': temperature}
            )

            # Aquí se podría añadir el _sanitize_ai_output si se decide que es necesario
            # para la salida del formateador de Markdown. Por ahora, se omite según el requerimiento.
            formatted_content = response['message']['content'].strip()
            sanitized_content = self._sanitize_ai_output(formatted_content, raw_note_content, title)
            return sanitized_content

        except Exception as e:
            print(f"Error formateando nota con Markdown usando OLLAMA: {e}")
            return raw_note_content # Devolver contenido en bruto en caso de error

    def _sanitize_ai_output(self, ai_content: str, original_plain_text: str, title: str) -> str:
        # Normalize line endings
        content = ai_content.replace('\r\n', '\n').replace('\r', '\n')

        # Strip leading/trailing whitespace from the whole content
        content = content.strip()

        # Normalize multiple newlines (3 or more) down to exactly two first.
        content = re.sub(r'\n{3,}', '\n\n', content)

        # Split into lines, strip each line.
        lines = [line.strip() for line in content.split('\n')]

        # Rejoin lines, ensuring that single newlines that are likely paragraph breaks become double,
        # while trying to preserve existing double newlines and list/header structures.
        processed_lines = []
        for i, line in enumerate(lines):
            processed_lines.append(line)
            if i < len(lines) - 1: # If it's not the last line
                # Check if the current line is not empty and the next line is not empty,
                # and the current line does not end a list item or header,
                # and the next line doesn't start one immediately (basic check).
                # This logic aims to convert single newlines between text blocks to double.
                if line and lines[i+1] and \
                   not (line.startswith(('* ')) or line.startswith(('- ')) or line.startswith('#')) and \
                   not (lines[i+1].startswith(('* ')) or lines[i+1].startswith(('- ')) or lines[i+1].startswith('#')):
                    # If the original separation was just one newline (after stripping and initial normalization)
                    # and now it's not followed by an immediate double newline in processed_lines.
                    # This part is tricky. Let's simplify:
                    # After stripping and reducing \n{3,} to \n\n,
                    # any single \n remaining between non-empty lines should become \n\n.
                    pass # The logic below will handle this better.

        content = '\n'.join(processed_lines)

        # Replace single newlines with double newlines, unless it's a list item, blockquote, or header.
        # This regex is more aggressive and should be applied carefully.
        # It looks for a newline that is NOT preceded or followed by another newline,
        # and is not followed by typical markdown list/header/blockquote markers.
        # This is run *after* stripping lines and initial \n{3,} normalization.
        # The goal is to make sure standard paragraphs are separated by \n\n.

        # First, ensure all existing intentional double newlines are preserved (or created if missing between "paragraphs")
        # A paragraph is roughly a block of text not starting with list/header markers.
        # This is complex. Let's try a simpler sequence:
        # 1. Normalize \r\n and \r to \n
        # 2. Strip leading/trailing whitespace from the whole string.
        # 3. Reduce 3+ newlines to 2: \n\n\n -> \n\n
        # 4. Strip whitespace from each line.
        # 5. Re-join. At this point, paragraphs might be separated by \n or \n\n.
        # 6. Convert single \n to \n\n if they are not part of a list-like structure.

        # Step 1 & 2 already done essentially with initial `content.strip()` and `replace`
        # Step 3:
        content = re.sub(r'\n{3,}', '\n\n', content) # Done again to be sure

        # Step 4 & 5:
        lines = [line.strip() for line in content.split('\n')]
        content = '\n'.join(lines) # Now lines are stripped, and only \n or \n\n separate them.

        # Step 6: Convert single \n to \n\n if not a list item etc.
        # This regex finds a single newline (not preceded or followed by another \n)
        # and ensures the line following it doesn't start with markdown list/header.
        # (?<!\n) - not preceded by \n
        # \n       - the single newline
        # (?!\n)   - not followed by \n
        # (?![\*\-#>\s]) - not followed by typical markdown structural characters or space (e.g. indented lists)
        # The negative lookahead (?![\*\-#>\s]) might be too broad.
        # Let's refine: we want to turn `foo\nbar` into `foo\n\nbar`
        # But not `* item1\n* item2` or `# H1\nContent`

        # Simpler approach: Split by \n then intelligently join with \n or \n\n
        new_content_parts = []
        for i, line in enumerate(lines):
            new_content_parts.append(line)
            if i < len(lines) - 1: # If there is a next line
                current_line_is_list_item = line.startswith(("* ", "- ", "+ ")) or re.match(r"^\d+\.\s", line)
                next_line_is_list_item = lines[i+1].startswith(("* ", "- ", "+ ")) or re.match(r"^\d+\.\s", lines[i+1])
                current_line_is_header = line.startswith("#")

                if current_line_is_list_item and next_line_is_list_item:
                    new_content_parts.append("\n") # Single newline between list items
                elif line == "" and lines[i+1] == "": # If we have two empty lines from original \n\n, preserve one \n\n effectively
                    if not (new_content_parts[-2] == "") : # Avoid creating more than \n\n from multiple blank lines
                       new_content_parts.append("\n")
                elif line and lines[i+1]: # Both current and next are non-empty
                    new_content_parts.append("\n\n") # Default to double newline for paragraph separation
                elif line and not lines[i+1]: # Current is non-empty, next is empty
                     new_content_parts.append("\n\n") # End of a paragraph before a blank line
                elif not line and lines[i+1]: # Current is empty, next is non-empty
                     # This implies an existing \n\n structure, so just ensure one \n before next content
                     if i > 0 and new_content_parts[-2] != "": # if previous was not empty
                         pass # \n\n already handled by previous line.
                     # else it's start of file or multiple blank lines, handled by strip and \n{3,}
                # else: single \n if one is empty, handled by previous logic or stripping

        content = "\n".join(new_content_parts)
        # Post-process to clean up:
        # Remove excessive blank lines again (more than two consecutive newlines down to two)
        content = re.sub(r'\n{3,}', '\n\n', content).strip()


        # Fallback for severely unformatted text
        # Check if it's still a long block without proper paragraph separation
        # Also, check if it contains at least some typical markdown structuring characters.
        # If not, it's likely the AI just returned a blob of text.
        is_likely_blob = len(content) > 300 and '\n\n' not in content
        has_markdown_chars = any(char in content for char in ['#', '>', '*', '-'])

        if is_likely_blob and not has_markdown_chars:
            print(f"ADVERTENCIA: AI output for title '{title}' appears unformatted after sanitization. Using fallback based on original plain text.")
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