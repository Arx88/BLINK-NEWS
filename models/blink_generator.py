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
import logging
# from models.image_generator import ImageGenerator # <-- LÍNEA COMENTADA
import ollama

# Setup logger
logger = logging.getLogger(__name__)

def setup_file_logger(log_dir_name="LOG"):
    if not logger.handlers: # Check if handlers are already configured
        logger.setLevel(logging.DEBUG) # Set logger level

        # Create log directory
        # Assuming /app is the WORKDIR in Dockerfile, so logs go to /app/LOG
        log_dir_path = os.path.join("/app", log_dir_name)
        os.makedirs(log_dir_path, exist_ok=True)

        # Create timestamped log file
        log_file_name = f"blink_run_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
        log_file_path = os.path.join(log_dir_path, log_file_name)

        # Create file handler
        file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)

        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)

        # Add handler to the logger
        logger.addHandler(file_handler)

        logger.info("File logger setup complete. Logging to: " + log_file_path)
    else:
        logger.info("File logger already configured.")

setup_file_logger() # Call it once at module level

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
                "prompt_template": '''Eres un asistente editorial experto. Se te proporcionará el texto de un artículo de noticias y un título. Tu tarea es transformar este texto en un artículo bien estructurado en formato Markdown.

El artículo en Markdown DEBE incluir los siguientes elementos en este orden:

1.  **Texto Principal del Artículo:**
    *   Revisa el texto original para asegurar una buena fluidez y estructura de párrafos.
    *   Utiliza saltos de línea dobles para separar párrafos en Markdown.
    *   Si el texto original contiene subtítulos implícitos o secciones, puedes usar encabezados Markdown (por ejemplo, `## Subtítulo Relevante`) si mejora la legibilidad. No inventes subtítulos si no son evidentes en el texto.

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

Título del Artículo Original:
{title}

Texto del Artículo Original (en texto plano):
{effective_plain_text_content}

Artículo Estructurado en Formato Markdown:'''
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
        self.ollama_client = ollama.Client(host=ollama_base_url, timeout=180)
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
            logger.error(f"Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return "general" # Or raise an error

        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

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
                        logger.debug(f"Determined category by explicit pattern: {best_match_category} from line: '{line}'")
                        # Return immediately as this is the highest confidence match
                        logger.debug(f"Determined category (final by explicit pattern): {best_match_category} (raw response: {raw_response_content[:200]})")
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
                logger.debug(f"Determined category by exact match on last line: {best_match_category}")
                # Return immediately
                logger.debug(f"Determined category (final by last line exact match): {best_match_category} (raw response: {raw_response_content[:200]})")
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
                    logger.debug(f"Determined category by whole word match in last line: {best_match_category}")
                    # Return immediately
                    logger.debug(f"Determined category (final by last line whole word): {best_match_category} (raw response: {raw_response_content[:200]})")
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
                    logger.debug(f"Determined category by broad substring search (fallback): {best_match_category}")

            logger.debug(f"Determined category (final): {best_match_category} (raw response snippet: {raw_response_content[:200]})")
            return best_match_category

        except ollama.ResponseError as e:
            logger.error(f"Error communicating with Ollama for category determination: {e.error}")
            return "general" # Fallback category
        except Exception as e:
            logger.error(f"Unexpected error in determine_category_with_ai: {e}")
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
            logger.error(f"Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return False, proposed_category # Or raise an error

        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

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
            logger.debug(f"Verification response for category '{proposed_category}' for title '{title}': {verification_response}")

            if "sí" in verification_response or "si" in verification_response: # Accept with or without accent
                return True, proposed_category
            elif "no" in verification_response:
                return False, proposed_category # Verification failed
            else:
                # Unclear response, treat as verification failed to be safe
                logger.debug(f"Unclear verification response. Defaulting to not verified.")
                return False, proposed_category

        except ollama.ResponseError as e:
            logger.error(f"Error communicating with Ollama for category verification: {e.error}")
            # If verification fails due to error, assume not verified
            return False, proposed_category
        except Exception as e:
            logger.error(f"Unexpected error in verify_category_with_ai: {e}")
            # If verification fails due to error, assume not verified
            return False, proposed_category

    def format_content_with_ai(self, plain_text_content: str, title: str) -> str:
        """
        Formatea el contenido de texto plano de un artículo a Markdown usando Ollama,
        incluyendo el cuerpo del artículo, una cita destacada y conclusiones clave.
        """
        logger.debug(f"Iniciando format_content_with_ai para título: {title}")
        if not plain_text_content:
            logger.debug(f"plain_text_content está vacío. Finalizando format_content_with_ai para título: {title}")
            return ""

        # Truncate plain_text_content for the prompt to avoid overly long inputs
        task_key = "format_main_content"
        task_config = self.ai_task_configs.get(task_key, {}) # This will now contain prompt_template and temperature
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars = task_config.get('input_max_chars', 20000)
        temperature = task_config.get('temperature', 0.6)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            logger.error(f"Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return plain_text_content # Or raise an error

        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        # This is the effective plain_text_content that will be used in the prompt.
        effective_plain_text_content = plain_text_content[:max_chars]
        # logger.debug(f"plain_text_content para formatear (primeros 500 chars): {effective_plain_text_content[:500]}") # Replaced by DEBUG_FORMAT_INPUT_TEXT

        prompt_variables = {
            "title": title,
            "effective_plain_text_content": effective_plain_text_content
        }
        prompt = prompt_template_str.format(**prompt_variables)

        logger.debug(f"Input plain_text_content (first 500 chars): {plain_text_content[:500]}")
        logger.debug(f"Full prompt being sent for formatting:\n{prompt}")

        try:
            logger.debug(f"Llamando a Ollama para FORMATEAR CONTENIDO para título: {title}. Modelo: {model_to_use}. Temperatura: {temperature}")
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': temperature}
            )
            logger.debug(f"Raw response from Ollama for formatting:\n{response}")
            raw_markdown_content = response['message']['content'].strip()

            # Cleanup <think>...</think> blocks from the beginning of the response
            cleaned_markdown_content = re.sub(r"^\s*<think>.*?</think>\s*", "", raw_markdown_content, flags=re.DOTALL | re.IGNORECASE)
            final_content = cleaned_markdown_content.strip()

            # Basic check if response looks like markdown (e.g. contains common markdown chars)
            if not any(char in final_content for char in ['#', '>', '*', '-']):
                logger.warning(f"AI response for content formatting (after cleanup) might not be Markdown for title '{title}'. Response: {final_content[:200]}")
            # *** NEW SANITIZATION CALL ***
            final_content = self._sanitize_ai_output(final_content, plain_text_content, title)

            # Basic check if response looks like markdown (e.g. contains common markdown chars)
            # This check is now less critical due to sanitization but can still be a log.
            if not any(char in final_content for char in ['#', '>', '*', '-']):
                logger.warning(f"AI response for content formatting (after sanitization) might not be Markdown for title '{title}'. Response: {final_content[:200]}")

            logger.debug(f"markdown_content generado y sanitizado (primeros 500 chars): {final_content[:500]}")
            logger.debug(f"Finalizando format_content_with_ai para título: {title}")
            return final_content
        except ollama.ResponseError as e:
            error_message = str(e.error) if hasattr(e, 'error') else str(e)
            # The following error logging for timeouts is maintained as it's specific and useful.
            if "timeout" in error_message.lower():
                logger.debug(f"TIMEOUT de Ollama (ResponseError) en format_content_with_ai para título '{title}': {error_message}")
            # General ResponseError log is now more specific
            logger.error(f"Ollama ResponseError during content formatting: {error_message}. Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            logger.debug(f"Finalizando format_content_with_ai para título: {title} (DEVOLVIENDO TEXTO PLANO SANITIZADO POR OLLAMA ResponseError)")
            # *** SANITIZE FALLBACK ***
            return self._sanitize_ai_output(plain_text_content, plain_text_content, title) # Sanitize the original text as fallback
        except Exception as e: # Catch other exceptions, including potential RequestError wrapping TimeoutException
            error_message = str(e)
            # The following error logging for timeouts is maintained as it's specific and useful.
            if "timeout" in error_message.lower():
                logger.debug(f"TIMEOUT (detectado en Exception genérica) en format_content_with_ai para título '{title}': {error_message}")
            # General Exception log is now more specific
            logger.error(f"Unexpected error during content formatting: {error_message}")
            logger.debug(f"Finalizando format_content_with_ai para título: {title} (DEVOLVIENDO TEXTO PLANO SANITIZADO POR Exception)")
            # *** SANITIZE FALLBACK ***
            return self._sanitize_ai_output(plain_text_content, plain_text_content, title) # Sanitize the original text as fallback

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
            logger.warning(f"AI output for title '{title}' appears unformatted after sanitization. Using fallback based on original plain text.")
            # Fallback to original plain text, trying to make paragraphs
            fallback_content = original_plain_text.replace('\r\n', '\n').replace('\r', '\n')
            fallback_lines = [line.strip() for line in fallback_content.split('\n') if line.strip()]
            return '\n\n'.join(fallback_lines)

        return content

    def generate_blink_from_news_group(self, news_group):
        """Genera un resumen en formato BLINK a partir de un grupo de noticias similares"""
        # Usar el título más representativo del grupo
        title = self.select_best_title(news_group)
        logger.debug(f"Iniciando generate_blink_from_news_group para título representativo: {title}")

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
                logger.error(f"Error al procesar URL {url}: {e}")

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

        logger.debug(f"combined_content (primeros 500 chars) para IA: {combined_content[:500]}")

        # Truncate combined_content before sending to AI for Markdown formatting
        # Max length for plain text to keep formatted Markdown likely under a certain size.
        # E.g. 10000 chars plain text -> perhaps ~12000-15000 Markdown.
        MAX_PLAIN_TEXT_LENGTH = 10000 # Configurable, or based on `format_main_content`'s input_max_chars

        if len(combined_content) > MAX_PLAIN_TEXT_LENGTH:
            logger.debug(f"Truncating combined_content from {len(combined_content)} to {MAX_PLAIN_TEXT_LENGTH} characters.")
            truncated_combined_content = combined_content[:MAX_PLAIN_TEXT_LENGTH]
        else:
            truncated_combined_content = combined_content

        # Formatear el contenido combinado (y truncado) a Markdown usando IA
        markdown_content = self.format_content_with_ai(truncated_combined_content, title)

        # Crear el objeto BLINK
        blink = {
            'id': blink_id,
            'title': title,
            'points': points,
            'image': image_url,
            'sources': list(set(sources)),
            'urls': urls,
            'timestamp': datetime.now().isoformat(),
            'content': markdown_content, # Truncation now happens on input to format_content_with_ai
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
            logger.error(f"Error al obtener contenido del artículo {url}: {e}")
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
            logger.error(f"Prompt template for '{task_key}' not found. Using a very basic fallback or skipping.")
            return self.generate_fallback_points(title, num_points) # Or raise an error

        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxChars={max_chars}, Temp={temperature}")

        if not text:
            return self.generate_fallback_points(title, num_points)

        truncated_text = text[:max_chars]
        # logger.debug(f"Texto para resumen (primeros 500 chars): {truncated_text[:500]}") # Replaced by DEBUG_SUMM_INPUT_TEXT

        prompt_variables = {
            "title": title,
            "num_points": num_points,
            "truncated_text": truncated_text
        }
        prompt = prompt_template_str.format(**prompt_variables)

        logger.debug(f"Input text (first 500 chars): {text[:500]}")
        logger.debug(f"Full prompt being sent:\n{prompt}")

        try:
            logger.debug(f"Llamando a Ollama para GENERAR PUNTOS para título: {title}. Modelo: {model_to_use}. Temperatura: {temperature}")
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
            logger.debug(f"Raw response from Ollama:\n{response}")
            summary_content = response['message']['content']
            logger.debug(f"Raw summary_content:\n{summary_content}") # Log the raw content

            # *** REVISED LOGIC TO HANDLE <think> BLOCK START ***
            think_block_end_tag = "</think>"
            idx_end_think = summary_content.rfind(think_block_end_tag) # Use rfind to get the last occurrence

            if idx_end_think != -1:
                actual_summary_text = summary_content[idx_end_think + len(think_block_end_tag):].strip()
                logger.debug(f"Text after <think> block (len {len(actual_summary_text)}):\n{actual_summary_text}")
            else:
                actual_summary_text = summary_content.strip()
                logger.debug(f"No <think> block found, using full content (len {len(actual_summary_text)}).")
            # *** REVISED LOGIC TO HANDLE <think> BLOCK END ***

            extracted_points = []
            if actual_summary_text: # Proceed only if there's text to parse
                all_lines = actual_summary_text.split('\n')
                logger.debug(f"Lines split for point extraction: {all_lines}")
                for line in all_lines:
                    # Remove common list markers and leading/trailing whitespace
                    cleaned_line = re.sub(r'^\s*([\*\-\+]\s*|\d+\.\s+)?', '', line).strip()
                    if cleaned_line: # Only add non-empty lines
                        extracted_points.append(cleaned_line)

            points = extracted_points[:num_points]
            logger.debug(f"Points extracted ({len(points)}): {points}")

            logger.debug(f"len(points) = {len(points)}, num_points = {num_points}, Condition (len(points) < num_points) is {len(points) < num_points}")
            if len(points) < num_points:
                logger.debug(f"Missing {num_points - len(points)} points, using fallbacks.")
                missing_points = num_points - len(points)
                fallback_points = self.generate_fallback_points(title, missing_points)
                points.extend(fallback_points)

            return points

        except ollama.ResponseError as e:
            logger.error(f"Ollama ResponseError during summary generation: {e.error}. Status code: {e.status_code if hasattr(e, 'status_code') else 'N/A'}")
            return self.generate_fallback_points(title, num_points)
        except Exception as e:
            logger.error(f"Unexpected error during summary generation: {str(e)}")
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