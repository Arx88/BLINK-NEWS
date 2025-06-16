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

    def __init__(self, app_config=None): # Added app_config parameter
        """Inicializa el generador de BLINKS"""
        self.app_config = app_config if app_config is not None else {}

        # Default AI task configurations with prompt templates
        default_task_configs = {
            "determine_category": {
                "model_name": "qwen3:32b", "input_max_chars": 1000, "temperature": 0.2,
                "prompt_template": """Analiza el siguiente texto de una noticia y clasifícalo en UNA de las siguientes categorías: {categories_str}.

Título: {title}
Texto:
{input_text_truncated}

Responde ÚNICAMENTE con el nombre de la categoría que mejor se ajuste al texto. No añadas ninguna explicación, puntuación o frase adicional.
Categoría:"""
            },
            "verify_category": {
                "model_name": "qwen3:32b", "input_max_chars": 1000, "temperature": 0.1,
                "prompt_template": """Se ha clasificado una noticia con el título "{title}" y el siguiente texto como perteneciente a la categoría "{proposed_category}".

Texto de la noticia:
{input_text_truncated}

¿Consideras que esta clasificación en la categoría "{proposed_category}" es correcta? Responde únicamente con "sí" o "no".
Respuesta:"""
            },
            "generate_summary_points": {
                "model_name": "qwen3:32b", "input_max_chars": 20000, "temperature": 0.3,
                "prompt_template": """A partir del siguiente texto de una noticia con el título "{title}", extrae exactamente {num_points} puntos clave.

  Reglas:
  - Cada punto debe ser una oración concisa y clara.
  - No incluyas frases introductorias, explicaciones o numeración.
  - Responde únicamente con los {num_points} puntos, cada uno en una nueva línea. NO INCLUYAS NINGÚN OTRO TEXTO, RAZONAMIENTO O CONVERSACIÓN. SOLO EMITE LA LISTA DE PUNTOS.

  Texto:
  {truncated_text}
  """
            },
            "format_main_content": {
                "model_name": "qwen3:32b", "input_max_chars": 20000, "temperature": 0.6,
                "prompt_template": """Eres un asistente editorial experto. Se te proporcionará el texto de un artículo de noticias y un título. Tu tarea es transformar este texto en un artículo bien estructurado en formato Markdown.

El artículo en Markdown DEBE incluir los siguientes elementos en este orden:

1.  **Texto Principal del Artículo:**
    *   El texto de entrada ({effective_plain_text_content}) puede ser una compilación de varias fuentes y podría necesitar una limpieza significativa.
    *   Tu principal objetivo es estructurarlo en párrafos coherentes y legibles.
    *   **Párrafos:** Utiliza saltos de línea dobles (presionar Enter dos veces) para separar párrafos en Markdown. Cada párrafo debe tratar una idea o tema principal. Evita párrafos excesivamente largos; si una sección de texto es muy extensa y no tiene pausas naturales, intenta dividirla lógicamente.
    *   **Fluidez:** Asegura una buena fluidez y cohesión entre párrafos.
    *   **Subtítulos:** Si el texto original contiene subtítulos implícitos o secciones claramente diferenciadas, puedes usar encabezados Markdown (por ejemplo, `## Subtítulo Relevante` o `### Sub-subtítulo`) para mejorar la organización. No inventes subtítulos si no son evidentes en el texto. Prioriza una buena estructura de párrafos sobre el uso excesivo de subtítulos.

2.  **Cita Destacada:**
    *   Identifica una frase o declaración impactante y relevante del texto original que pueda servir como cita.
    *   Formatea esta cita como un blockquote en Markdown (usando `>`).
    *   Si es posible atribuir la cita a una persona o fuente mencionada en el texto, añade la atribución después del blockquote en una línea separada, por ejemplo:
        `> Esta es la cita impactante.`
        `
        - Nombre de la Persona o Fuente`

3.  **Conclusiones Clave:**
    *   Al final del artículo, incluye una sección titulada `## Conclusiones Clave`.
    *   Debajo de este encabezado, presenta una lista de 3 a 5 puntos clave o conclusiones derivados del artículo.
    *   Formatea estos puntos como una lista de viñetas en Markdown (usando `*` o `-` para cada punto).

**Consideraciones Adicionales para el Markdown:**
*   Asegúrate de que todo el resultado sea un único bloque de texto en Markdown válido.
*   No añadas ningún comentario, introducción o texto explicativo fuera del propio contenido del artículo en Markdown.
*   El objetivo es tomar el texto plano proporcionado y enriquecerlo estructuralmente usando Markdown.
*   Presta especial atención a la correcta formación de párrafos. El contenido NO debe ser un solo bloque de texto. Separa las ideas en párrafos distintos usando dos saltos de línea.

Título del Artículo Original:
{title}

Texto del Artículo Original (en texto plano):
{effective_plain_text_content}

Artículo Estructurado en Formato Markdown:"""
            }
        }

        # Merge with configurations from app_config if available
        self.ai_task_configs = {k: v.copy() for k, v in default_task_configs.items()} # Deep copy defaults
        ext_task_configs = self.app_config.get('ai_task_configs', {})
        for task_name, task_cfg in ext_task_configs.items():
            if task_name in self.ai_task_configs:
                self.ai_task_configs[task_name].update(task_cfg)
            else:
                # Allow new tasks to be defined entirely in config.json
                self.ai_task_configs[task_name] = task_cfg.copy()


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
        self.ollama_client = ollama.Client(host=ollama_base_url, timeout=90)
        # self.ollama_model is now a general fallback, specific models are in ai_task_configs
        self.ollama_model = self.app_config.get('default_ollama_model_name', 'qwen3:32b')


    def determine_category_with_ai(self, text_content, title):
        task_key = "determine_category"
        task_config = self.ai_task_configs.get(task_key, {}) # This will now contain prompt_template and temperature
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars = task_config.get('input_max_chars', 1000)
        temperature = task_config.get('temperature', 0.2)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            # Fallback or error if template is crucial and not found
            print(f"ERROR_BLINK_GEN: Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return "general" # Or raise an error

        print(f"DEBUG_BLINK_GEN: Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        if not text_content and not title:
            return "general" # Not enough info to determine category

        # Combine title and content for better context, prioritizing content
        input_text_combined = text_content if text_content else ""
        if title:
            input_text_combined = title + "\n\n" + input_text_combined

        input_text_truncated = input_text_combined[:max_chars]

        categories_str = ", ".join(ALLOWED_CATEGORIES)

        prompt_variables = {
            "categories_str": categories_str,
            "title": title,
            "input_text_truncated": input_text_truncated
        }
        prompt = prompt_template_str.format(**prompt_variables)

        try:
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': temperature}
            )

            # Ensure 're' is imported at the top of the file: import re
            raw_response_content = response['message']['content'].strip()
            lines = raw_response_content.split('\n')

            best_match_category = "general" # Default category

            # 1. Try to find an explicit "categoría: <category>" or "category: <category>" pattern
            explicit_category_pattern = r"(?:categor[ií]a|category):\s*([\w\-]+)"
            for line in reversed(lines): # Check last lines first
                match = re.search(explicit_category_pattern, line, re.IGNORECASE)
                if match:
                    extracted_cat = match.group(1).strip().lower()
                    # Further clean common non-alphanumeric if model includes them
                    extracted_cat = re.sub(r"[^a-záéíóúñü\s-]", "", extracted_cat)
                    extracted_cat = extracted_cat.strip()
                    if extracted_cat in ALLOWED_CATEGORIES:
                        best_match_category = extracted_cat
                        print(f"DEBUG: Determined category by explicit pattern: {best_match_category} from line: '{line}'")
                        # Return immediately as this is the highest confidence match
                        print(f"DEBUG: Determined category (final by explicit pattern): {best_match_category} (raw response: {raw_response_content[:200]})")
                        return best_match_category

            # 2. If no explicit pattern, check the last non-empty line for an exact match from ALLOWED_CATEGORIES
            last_line_text = ""
            for line in reversed(lines):
                cleaned_line = line.strip().lower()
                # Further clean common non-alphanumeric if model includes them
                cleaned_line = re.sub(r"[^a-záéíóúñü\s-]", "", cleaned_line)
                cleaned_line = cleaned_line.strip()
                if cleaned_line: # Found the last non-empty line
                    last_line_text = cleaned_line
                    break

            if last_line_text in ALLOWED_CATEGORIES:
                best_match_category = last_line_text
                print(f"DEBUG: Determined category by exact match on last line: {best_match_category}")
                # Return immediately
                print(f"DEBUG: Determined category (final by last line exact match): {best_match_category} (raw response: {raw_response_content[:200]})")
                return best_match_category

            # 3. Fallback: Check if any ALLOWED_CATEGORIES is a whole word match in the cleaned last line
            if last_line_text:
                found_cats_in_last_line = []
                for cat_option in ALLOWED_CATEGORIES:
                    # Regex for whole word matching: (?:^|\s)cat_option(?:$|\s)
                    if re.search(r"(?:^|\s)" + re.escape(cat_option) + r"(?:$|\s)", last_line_text):
                        found_cats_in_last_line.append(cat_option)

                if found_cats_in_last_line:
                    found_cats_in_last_line.sort(key=len, reverse=True)
                    best_match_category = found_cats_in_last_line[0]
                    print(f"DEBUG: Determined category by whole word match in last line: {best_match_category}")
                    # Return immediately
                    print(f"DEBUG: Determined category (final by last line whole word): {best_match_category} (raw response: {raw_response_content[:200]})")
                    return best_match_category

            # 4. Final Fallback (Original broader substring search across the entire raw response - use with caution)
            if best_match_category == "general": # Only if other methods failed
                potential_matches = []
                # Clean the whole response content for this broader search too
                cleaned_raw_response = re.sub(r"[^a-záéíóúñü\s-]", "", raw_response_content.lower()).strip()
                for cat_option in ALLOWED_CATEGORIES:
                    if cat_option in cleaned_raw_response: # Substring check
                        potential_matches.append(cat_option)
                if potential_matches:
                    potential_matches.sort(key=len, reverse=True)
                    best_match_category = potential_matches[0]
                    print(f"DEBUG: Determined category by broad substring search (fallback): {best_match_category}")

            print(f"DEBUG: Determined category (final): {best_match_category} (raw response snippet: {raw_response_content[:200]})")
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

        task_key = "verify_category"
        task_config = self.ai_task_configs.get(task_key, {}) # This will now contain prompt_template and temperature
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars = task_config.get('input_max_chars', 1000)
        temperature = task_config.get('temperature', 0.1)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            print(f"ERROR_BLINK_GEN: Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return False, proposed_category # Or raise an error

        print(f"DEBUG_BLINK_GEN: Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        # Combine title and content for better context, prioritizing content
        input_text_combined = text_content if text_content else ""
        if title:
            input_text_combined = title + "\n\n" + input_text_combined

        input_text_truncated = input_text_combined[:max_chars]

        prompt_variables = {
            "title": title,
            "proposed_category": proposed_category,
            "input_text_truncated": input_text_truncated
        }
        prompt = prompt_template_str.format(**prompt_variables)

        try:
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': temperature}
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

    def format_content_with_ai(self, plain_text_content: str, title: str) -> str:
        """
        Formatea el contenido de texto plano de un artículo a Markdown usando Ollama,
        incluyendo el cuerpo del artículo, una cita destacada y conclusiones clave.
        """
        print(f"DEBUG_BLINK_GEN: Iniciando format_content_with_ai para título: {title}")
        if not plain_text_content:
            print(f"DEBUG_BLINK_GEN: plain_text_content está vacío. Finalizando format_content_with_ai para título: {title}")
            return ""

        # Truncate plain_text_content for the prompt to avoid overly long inputs
        task_key = "format_main_content"
        task_config = self.ai_task_configs.get(task_key, {}) # This will now contain prompt_template and temperature
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars = task_config.get('input_max_chars', 20000)
        temperature = task_config.get('temperature', 0.6)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            print(f"ERROR_BLINK_GEN: Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return plain_text_content # Or raise an error

        print(f"DEBUG_BLINK_GEN: Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        # This is the effective plain_text_content that will be used in the prompt.
        effective_plain_text_content = plain_text_content[:max_chars]
        print(f"DEBUG_BLINK_GEN: plain_text_content para formatear (primeros 500 chars): {effective_plain_text_content[:500]}")

        prompt_variables = {
            "title": title,
            "effective_plain_text_content": effective_plain_text_content
        }
        prompt = prompt_template_str.format(**prompt_variables)

        try:
            print(f"DEBUG_BLINK_GEN: Llamando a Ollama para FORMATEAR CONTENIDO para título: {title}. Modelo: {model_to_use}. Temperatura: {temperature}")
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': temperature}
            )
            print(f"DEBUG_BLINK_GEN: Ollama RESPONDIÓ para FORMATEAR CONTENIDO para título: {title}. Respuesta (primeros 100 chars): {response['message']['content'][:100] if response and response.get('message') else 'Respuesta vacía o inválida'}") # Already good
            raw_markdown_content = response['message']['content'].strip()

            # Cleanup <think>...</think> blocks from the beginning of the response
            cleaned_markdown_content = re.sub(r"^\s*<think>.*?</think>\s*", "", raw_markdown_content, flags=re.DOTALL | re.IGNORECASE)
            final_content = cleaned_markdown_content.strip()

            # Basic check if response looks like markdown (e.g. contains common markdown chars)
            if not any(char in final_content for char in ['#', '>', '*', '-']):
                print(f"Warning: AI response for content formatting (after cleanup) might not be Markdown for title '{title}'. Response: {final_content[:200]}")
            # *** NEW SANITIZATION CALL ***
            final_content = self._sanitize_ai_output(final_content, plain_text_content, title)

            # Basic check if response looks like markdown (e.g. contains common markdown chars)
            # This check is now less critical due to sanitization but can still be a log.
            if not any(char in final_content for char in ['#', '>', '*', '-']):
                print(f"Warning: AI response for content formatting (after sanitization) might not be Markdown for title '{title}'. Response: {final_content[:200]}")

            print(f"DEBUG_BLINK_GEN: markdown_content generado y sanitizado (primeros 500 chars): {final_content[:500]}")
            print(f"DEBUG_BLINK_GEN: Finalizando format_content_with_ai para título: {title}")
            return final_content
        except ollama.ResponseError as e:
            error_message = str(e.error) if hasattr(e, 'error') else str(e)
            if "timeout" in error_message.lower():
                print(f"DEBUG_BLINK_GEN: TIMEOUT de Ollama (ResponseError) en format_content_with_ai para título '{title}': {error_message}")
            else:
                print(f"DEBUG_BLINK_GEN: Ollama ResponseError en format_content_with_ai para título '{title}': {error_message}")
            print(f"DEBUG_BLINK_GEN: Finalizando format_content_with_ai para título: {title} (DEVOLVIENDO TEXTO PLANO SANITIZADO POR OLLAMA ResponseError)")
            # *** SANITIZE FALLBACK ***
            return self._sanitize_ai_output(plain_text_content, plain_text_content, title) # Sanitize the original text as fallback
        except Exception as e: # Catch other exceptions, including potential RequestError wrapping TimeoutException
            error_message = str(e)
            if "timeout" in error_message.lower():
                print(f"DEBUG_BLINK_GEN: TIMEOUT (detectado en Exception genérica) en format_content_with_ai para título '{title}': {error_message}")
            else:
                print(f"DEBUG_BLINK_GEN: Excepción INESPERADA en format_content_with_ai para título '{title}': {error_message}")
            print(f"DEBUG_BLINK_GEN: Finalizando format_content_with_ai para título: {title} (DEVOLVIENDO TEXTO PLANO SANITIZADO POR Exception)")
            # *** SANITIZE FALLBACK ***
            return self._sanitize_ai_output(plain_text_content, plain_text_content, title) # Sanitize the original text as fallback

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
            print(f"Warning: AI output for title '{title}' appears unformatted after sanitization. Using fallback based on original plain text.")
            # Fallback to original plain text, trying to make paragraphs
            fallback_content = original_plain_text.replace('\r\n', '\n').replace('\r', '\n')
            fallback_lines = [line.strip() for line in fallback_content.split('\n') if line.strip()]
            return '\n\n'.join(fallback_lines)

        return content

    def generate_blink_from_news_group(self, news_group):
        """Genera un resumen en formato BLINK a partir de un grupo de noticias similares"""
        # Usar el título más representativo del grupo
        title = self.select_best_title(news_group)
        print(f"DEBUG_BLINK_GEN: Iniciando generate_blink_from_news_group para título representativo: {title}")

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

        print(f"DEBUG_BLINK_GEN: combined_content (primeros 500 chars) para IA: {combined_content[:500]}")
        # Formatear el contenido combinado a Markdown usando IA
        markdown_content = self.format_content_with_ai(combined_content, title)

        # Crear el objeto BLINK
        blink = {
            'id': blink_id,
            'title': title,
            'points': points,
            'image': image_url,
            'sources': list(set(sources)),
            'urls': urls,
            'timestamp': datetime.now().isoformat(),
            'content': markdown_content[:15000], # Apply truncation to the formatted Markdown content
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
    
    def generate_ollama_summary(self, text, title="", num_points=5): # text here is combined_content
        """Genera un resumen de 5 puntos clave usando Ollama."""
        task_key = "generate_summary_points"
        task_config = self.ai_task_configs.get(task_key, {}) # This will now contain prompt_template and temperature
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars = task_config.get('input_max_chars', 20000)
        temperature = task_config.get('temperature', 0.3)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            print(f"ERROR_BLINK_GEN: Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return self.generate_fallback_points(title, num_points) # Or raise an error

        print(f"DEBUG_BLINK_GEN: Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        if not text:
            return self.generate_fallback_points(title, num_points)

        truncated_text = text[:max_chars]
        print(f"DEBUG_BLINK_GEN: Texto para resumen (primeros 500 chars): {truncated_text[:500]}")

        prompt_variables = {
            "title": title,
            "num_points": num_points,
            "truncated_text": truncated_text
        }
        prompt = prompt_template_str.format(**prompt_variables)

        try:
            print(f"DEBUG_BLINK_GEN: Llamando a Ollama para GENERAR PUNTOS para título: {title}. Modelo: {model_to_use}. Temperatura: {temperature}")
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[
                    {
                        'role': 'user',
                        'content': prompt,
                    },
                ],
                options={'temperature': temperature}
            )
            print(f"DEBUG_BLINK_GEN: Ollama RESPONDIÓ para GENERAR PUNTOS para título: {title}. Respuesta (primeros 100 chars): {response['message']['content'][:100] if response and response.get('message') else 'Respuesta vacía o inválida'}") # Already good
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