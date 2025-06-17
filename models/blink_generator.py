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
from string import Template
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

        # Load external AI task configurations from config.json
        external_ai_configs = {}
        try:
            # Assuming config.json is in the parent directory of the 'models' directory
            config_path = os.path.join(os.path.dirname(__file__), '..', 'config.json')
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    loaded_config_json = json.load(f)
                    if 'ai_task_configs' in loaded_config_json:
                        external_ai_configs = loaded_config_json['ai_task_configs']
                        logger.info(f"Successfully loaded ai_task_configs from {config_path}")
                    else:
                        logger.warning(f"'ai_task_configs' not found in {config_path}. Using defaults.")
            else:
                logger.warning(f"{config_path} not found. Using default AI task configurations.")
        except FileNotFoundError:
            logger.warning(f"config.json not found at {config_path}. Using default AI task configurations.")
        except json.JSONDecodeError:
            logger.error(f"Error decoding config.json at {config_path}. Using default AI task configurations.")
        except Exception as e:
            logger.error(f"An unexpected error occurred while loading config.json: {e}. Using defaults.")

        if 'ai_task_configs' not in self.app_config:
            self.app_config['ai_task_configs'] = {}
        # Merge external_ai_configs into self.app_config['ai_task_configs'], giving precedence to external_ai_configs
        self.app_config['ai_task_configs'].update(external_ai_configs)


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
            "generate_blink_base_text": {
                "model_name": "qwen3:32b", # Default model, can be overridden by config.json
                "input_max_chars": 15000, # Max input characters for base text generation
                "temperature": 0.5,
                "prompt_template": """A partir del siguiente texto de varias noticias (cuyo título general es "{title}" y se proporciona solo para tu contexto), genera un único texto base coherente y conciso. Este texto base servirá como cuerpo principal para un resumen tipo Blink.

Reglas para el Texto Base:
-   Debe ser fluido y estar bien escrito.
-   **IMPORTANTE: El título del artículo (que es '{title}') es solo para tu contexto y NO debe ser incluido ni repetido en el texto base que generes.** El texto base debe comenzar directamente con la narrativa periodística.
-   NO DEBE INCLUIR NINGÚN FORMATO MARKDOWN (como encabezados, negritas, itálicas, citas, o listas).
-   NO intentes identificar, separar o formatear citas destacadas. Simplemente extrae y redacta el contenido periodístico principal.
-   Debe ser solo texto plano, listo para ser formateado en un paso posterior.

Texto de las noticias:
{input_text_truncated}

Texto base para Blink (solo texto plano, comenzando directamente con la narrativa periodística sin repetir el título '{title}', sin formato Markdown, sin secciones de citas):"""
            },
            "format_main_content": {
                "model_name": "qwen3:32b", "input_max_chars": 20000, "temperature": 0.6, # Max input for the formatter
                "prompt_template": '''Eres un asistente editorial experto. Se te proporcionará el texto de un artículo de noticias y un título. Tu tarea es transformar este texto en un artículo bien estructurado en formato Markdown.

El artículo en Markdown DEBE incluir los siguientes elementos en este orden:

1.  **Contenido Principal del Artículo (Cuerpo del Texto):**
    *   Revisa el texto original para asegurar una buena fluidez y estructura de párrafos.
    *   Utiliza saltos de línea dobles para separar párrafos en Markdown.
    *   Si el texto original contiene subtítulos implícitos o secciones, puedes usar encabezados Markdown (por ejemplo, `## Subtítulo Relevante`) si mejora la legibilidad. No inventes subtítulos si no son evidentes en el texto.
    *   IMPORTANTE: No repitas el título del artículo (que se te proporciona en la variable '{title}') al inicio del cuerpo del texto. El contenido debe comenzar directamente con la narrativa periodística.

2.  **Cita Destacada:**
    *   Identifica una **cita textual directa** del texto original que sea impactante y relevante. Idealmente, esta cita debería estar **atribuida explícitamente a una persona o fuente específica mencionada en el texto, o aparecer claramente entrecomillada en el texto original.** Si no se encuentra una cita textual clara que cumpla estos criterios, es preferible omitir la sección de Cita Destacada.
    *   Formatea esta cita como un blockquote en Markdown (usando `>`).
    *   Si es posible atribuir la cita a una persona o fuente mencionada en el texto, añade la atribución después del blockquote en una línea separada, por ejemplo:
        `> Esta es la cita impactante.`
        `> — Nombre de la Persona o Fuente`

3.  **Conclusiones Clave (como lista de puntos):**
    *   Al final del artículo, utiliza el encabezado `## Conclusiones Clave`.
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

        # Initialize self.ai_task_configs by deep copying default_task_configs
        self.ai_task_configs = {k: v.copy() for k, v in default_task_configs.items()}

        # Merge configurations from self.app_config['ai_task_configs'] (which now includes config.json content)
        # into self.ai_task_configs. self.app_config['ai_task_configs'] takes precedence.
        loaded_app_configs = self.app_config.get('ai_task_configs', {})
        for task_name, task_cfg in loaded_app_configs.items():
            if task_name in self.ai_task_configs:
                self.ai_task_configs[task_name].update(task_cfg)
            else:
                self.ai_task_configs[task_name] = task_cfg.copy() # Add as a new task if not in defaults


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
        template = Template(prompt_template_str)
        prompt = template.substitute(**prompt_variables)

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

    def _generate_blink_base_content(self, combined_content: str, title: str) -> str:
        """Genera el texto base para un Blink (sin formato Markdown) usando Ollama."""
        task_key = "generate_blink_base_text"
        task_config = self.ai_task_configs.get(task_key, {})
        model_to_use = task_config.get('model_name', self.ollama_model)
        max_chars_input = task_config.get('input_max_chars', 15000) # Max input for this specific task
        temperature = task_config.get('temperature', 0.5)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            logger.error(f"Prompt template for '{task_key}' not found. Returning original content.")
            return combined_content

        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxCharsInput={max_chars_input}, Temp={temperature}")

        input_text_truncated = combined_content[:max_chars_input]

        prompt_variables = {
            "title": title,
            "input_text_truncated": input_text_truncated
        }
        template = Template(prompt_template_str)
        prompt = template.substitute(**prompt_variables)
        logger.debug(f"Full prompt for '{task_key}':\n{prompt}")

        try:
            logger.debug(f"Llamando a Ollama para '{task_key}' para título: {title}. Modelo: {model_to_use}.")
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': temperature}
            )
            base_text = response['message']['content'].strip()
            logger.debug(f"Texto base generado para '{title}' (primeros 300 chars): {base_text[:300]}")
            return base_text
        except ollama.ResponseError as e:
            logger.error(f"Ollama ResponseError during '{task_key}' for '{title}': {e.error}")
            return combined_content # Fallback to original combined content
        except Exception as e:
            logger.error(f"Unexpected error during '{task_key}' for '{title}': {e}")
            return combined_content # Fallback

    def format_content_with_ai(self, base_text_content: str, title: str) -> str:
        """
        Formatea el texto base de un Blink a Markdown usando Ollama,
        incluyendo cuerpo, cita destacada y conclusiones clave.
        Utiliza la configuración de 'format_main_content'.
        """
        logger.debug(f"Iniciando format_content_with_ai (Markdown) para título: {title}")
        if not base_text_content:
            logger.warning(f"base_text_content está vacío para formatear. Título: {title}")
            return ""

        task_key = "format_main_content" # This task is for detailed Markdown formatting
        task_config = self.ai_task_configs.get(task_key, {})
        model_to_use = task_config.get('model_name', self.ollama_model)
        # Max input for the formatter itself, base_text_content should already be somewhat condensed.
        max_chars_formatter_input = task_config.get('input_max_chars', 20000)
        temperature = task_config.get('temperature', 0.6)
        prompt_template_str = task_config.get('prompt_template')

        if not prompt_template_str:
            logger.error(f"Prompt template for '{task_key}' not found. Returning base text content without formatting.")
            # Sanitize the base text as a fallback, as it might be used directly
            return self._sanitize_ai_output(base_text_content, base_text_content, title)


        logger.debug(f"Using config for '{task_key}': Model={model_to_use}, MaxCharsFormatterInput={max_chars_formatter_input}, Temp={temperature}")

        effective_plain_text_content = base_text_content[:max_chars_formatter_input]

        prompt_variables = {
            "title": title,
            "effective_plain_text_content": effective_plain_text_content # This is the base text
        }
        template = Template(prompt_template_str)
        prompt = template.substitute(**prompt_variables)
        logger.debug(f"Full prompt for '{task_key}':\n{prompt}")


        try:
            logger.debug(f"Llamando a Ollama para FORMATEAR A MARKDOWN ('{task_key}') para título: {title}. Modelo: {model_to_use}.")
            response = self.ollama_client.chat(
                model=model_to_use,
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': temperature}
            )
            raw_markdown_content = response['message']['content'].strip()

            # Cleanup <think>...</think> blocks (if any model uses them)
            cleaned_markdown_content = re.sub(r"^\s*<think>.*?</think>\s*", "", raw_markdown_content, flags=re.DOTALL | re.IGNORECASE)

            final_content = self._sanitize_ai_output(cleaned_markdown_content, base_text_content, title)
            logger.debug(f"Markdown content generado y sanitizado para '{title}' (primeros 300 chars): {final_content[:300]}")
            return final_content
        except ollama.ResponseError as e:
            logger.error(f"Ollama ResponseError during Markdown formatting ('{task_key}') for '{title}': {e.error}")
            return self._sanitize_ai_output(base_text_content, base_text_content, title) # Sanitize base as fallback
        except Exception as e:
            logger.error(f"Unexpected error during Markdown formatting ('{task_key}') for '{title}': {e}")
            return self._sanitize_ai_output(base_text_content, base_text_content, title) # Sanitize base as fallback

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
                # Add variables for blockquote check
                current_line_is_blockquote = line.startswith(">")
                next_line_is_blockquote = lines[i+1].startswith(">")

                if current_line_is_list_item and next_line_is_list_item:
                    new_content_parts.append("\n") # Single newline between list items
                elif current_line_is_blockquote and next_line_is_blockquote: # New condition
                    new_content_parts.append("\n") # Single newline between blockquote lines
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

    def _polish_markdown_output(self, markdown_content: str, title: str) -> str:
        """
        Refina el contenido Markdown generado por la IA para corregir problemas comunes
        de formato antes de que se considere final.
        """
        content = markdown_content
        logger.debug(f"Iniciando _polish_markdown_output para título: '{title}' (Primeros 100 chars de entrada: '{content[:100]}')")

        # 1. Eliminar título repetido al inicio, si está seguido por "==="
        # El título puede tener caracteres especiales de regex, por lo que se escapa.
        escaped_title = re.escape(title)
        # Patrón: Opcional "**" + título escapado + opcional "**" +
        #          una o más newlines y espacios opcionales alrededor de ellas +
        #          línea de === + cero o más newlines y espacios opcionales.
        # Usar count=1 para reemplazar solo la primera ocurrencia al inicio.
        pattern_title_separator = re.compile(
            r"^(?:\*\*)?" + escaped_title + r"(?:\*\*)?\s*[\r\n]+\s*={3,}\s*[\r\n]*",
            re.IGNORECASE # No se usa MULTILINE aquí porque ^ ya se refiere al inicio del string completo.
        )
        original_length = len(content)
        content = pattern_title_separator.sub("", content, count=1)
        if len(content) != original_length:
            logger.debug(f"Título con separador '===' eliminado. (Primeros 100 chars: '{content[:100]}')")
        else:
            logger.debug(f"Título con separador '===' no encontrado/eliminado. (Primeros 100 chars: '{content[:100]}')")

        # 2. Transformar "Conclusiones Clave" de Setext H1 a ATX H2
        # Busca "Conclusiones Clave" en una línea, seguida por "===" en la siguiente.
        pattern_conclusiones_setext = re.compile(
            r"^(Conclusiones Clave)\s*[\r\n]+\s*={3,}\s*[\r\n]*",
            re.IGNORECASE | re.MULTILINE
        )
        original_length = len(content)
        content = pattern_conclusiones_setext.sub("## Conclusiones Clave\n", content)
        if len(content) != original_length:
            logger.debug(f"'Conclusiones Clave' Setext H1 transformado a ATX H2. (Primeros 100 chars: '{content[:100]}')")

        # 3. Corregir duplicados de "Conclusiones Clave" y asegurar formato de encabezado
        # Caso A: "Conclusiones Clave\n## Conclusiones Clave\n" (texto plano antes de ATX)
        # Esto es más específico que el Caso B y debe ir primero.
        pattern_plain_then_correct_header = re.compile(
            r"^(?:\*\*)?Conclusiones Clave(?:\*\*)?\s*[\r\n]+\s*(## Conclusiones Clave)",
            re.IGNORECASE | re.MULTILINE
        )
        original_length = len(content)
        content = pattern_plain_then_correct_header.sub(r"\1", content) # Mantiene el encabezado ATX correcto
        if len(content) != original_length:
            logger.debug(f"Texto plano 'Conclusiones Clave' antes de ATX H2 eliminado. (Primeros 100 chars: '{content[:100]}')")

        # Caso B: Dos instancias de "Conclusiones Clave" en texto plano, separadas por nueva línea.
        # Esto podría ser "Conclusiones Clave\nConclusiones Clave" que no fue capturado por Setext H1.
        # Se convierte a un solo encabezado ATX H2.
        # Esta regla es más general y debe ir después de las transformaciones a ATX H2.
        # Usar \s*[\r\n]+\s* para flexibilidad con espacios y múltiples líneas vacías.
        pattern_double_plain_conclusion = re.compile(
            r"^(?:\*\*)?Conclusiones Clave(?:\*\*)?\s*[\r\n]+\s*(?:\*\*)?Conclusiones Clave(?:\*\*)?\s*[\r\n]+",
            re.IGNORECASE | re.MULTILINE
        )
        original_length = len(content)
        # Solo reemplaza si no hay ya un "## Conclusiones Clave" inmediatamente después, para evitar sobre-corrección.
        # Esta condición es difícil de poner en el regex de forma eficiente sin lookarounds complejos.
        # Por ahora, se asume que si esto ocurre, es un error a corregir a "## Conclusiones Clave".
        if pattern_double_plain_conclusion.search(content):
             # Antes de reemplazar, verificar si el área que sigue NO es ya un "## Conclusiones Clave"
            match = pattern_double_plain_conclusion.search(content)
            if match:
                # Si lo que sigue al match NO es "## Conclusiones Clave"
                following_text_start = match.end()
                if not content[following_text_start:].strip().startswith("## Conclusiones Clave"):
                    content = pattern_double_plain_conclusion.sub("## Conclusiones Clave\n", content, count=1) # count=1 para evitar loops si el patrón es muy voraz
                    logger.debug(f"Duplicado de texto plano 'Conclusiones Clave' transformado a ATX H2. (Primeros 100 chars: '{content[:100]}')")

        # 4. Eliminar líneas separadoras huérfanas ("====" o "----")
        lines = content.splitlines()
        polished_lines = []
        for i, line_text in enumerate(lines):
            stripped_line = line_text.strip()
            is_separator_line = re.fullmatch(r"={3,}|-{3,}", stripped_line)
            if is_separator_line:
                if i > 0 and lines[i-1].strip() and not re.fullmatch(r"={3,}|-{3,}", lines[i-1].strip()):
                    polished_lines.append(line_text)
                else:
                    logger.debug(f"Eliminando línea separadora huérfana: '{line_text}'")
            else:
                polished_lines.append(line_text)
        content = "\n".join(polished_lines)

        # Asegurar un solo salto de línea al final si el contenido no está vacío y no tiene ya uno.
        if content.strip() and not content.endswith("\n"):
            content += "\n"
        # Remover múltiples saltos de línea al final, dejando solo uno si hay contenido.
        if content.strip():
             content = re.sub(r"[\r\n]+$", "\n", content)
        else: # Si el contenido es solo whitespace (o vacío) después de las operaciones
            content = "" # Devolver string vacío

        logger.debug(f"_polish_markdown_output finalizado para título: '{title}' (Primeros 100 chars de salida: '{content[:100]}')")
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

        logger.debug(f"Combined_content (primeros 500 chars) para IA: {combined_content[:500]}")

        # Truncate combined_content before sending to AI for base text generation
        # This uses the input_max_chars from the 'generate_blink_base_text' task if defined, else a default.
        base_text_task_cfg = self.ai_task_configs.get("generate_blink_base_text", {})
        MAX_INPUT_FOR_BASE_GENERATION = base_text_task_cfg.get("input_max_chars", 15000)

        if len(combined_content) > MAX_INPUT_FOR_BASE_GENERATION:
            logger.debug(f"Truncating combined_content from {len(combined_content)} to {MAX_INPUT_FOR_BASE_GENERATION} for base text generation.")
            truncated_combined_content = combined_content[:MAX_INPUT_FOR_BASE_GENERATION]
        else:
            truncated_combined_content = combined_content

        logger.info(f"Generando texto base para Blink: {title}")
        base_content = self._generate_blink_base_content(truncated_combined_content, title)

        logger.info(f"Formateando a Markdown el texto base para Blink: {title}")
        markdown_content = self.format_content_with_ai(base_content, title)

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
        template = Template(prompt_template_str)
        prompt = template.substitute(**prompt_variables)

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