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
# from models.image_generator import ImageGenerator # Original import
import ollama

try:
    from models.image_generator import ImageGenerator
    IMAGE_GENERATOR_AVAILABLE_SNG = True # Use a distinct name for the flag
    print("[SuperiorNoteGenerator] ImageGenerator loaded successfully.")
except ModuleNotFoundError:
    ImageGenerator = None # Define ImageGenerator as None if module is not found
    IMAGE_GENERATOR_AVAILABLE_SNG = False
    print("[SuperiorNoteGenerator] WARNING: 'models.image_generator' not found. Image generation feature will be disabled for superior notes.")
except ImportError as e: # Catch other import errors too
    ImageGenerator = None
    IMAGE_GENERATOR_AVAILABLE_SNG = False
    print(f"[SuperiorNoteGenerator] WARNING: Could not import 'models.image_generator' due to an ImportError: {e}. Image generation feature will be disabled for superior notes.")

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
        if IMAGE_GENERATOR_AVAILABLE_SNG:
            self.image_generator = ImageGenerator()
        else:
            self.image_generator = None
        
        # Inicializar el cliente de Ollama
        self.ollama_client = ollama.Client(host='http://localhost:11434')
        self.ollama_model = 'llama3'  # Modelo por defecto
    
    def generate_superior_note(self, articles_group, topic):
        """
        Genera una nota superior a partir de múltiples artículos sobre el mismo tema
        
        Args:
            articles_group (list): Lista de artículos sobre el mismo tema
            topic (str): Tema principal
            
        Returns:
            dict: Nota superior con contenido completo y resumen ultra breve
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
        image_url = None # Default to None
        if self.image_generator:
            print("[SuperiorNoteGenerator] Attempting to generate image with ImageGenerator...")
            try:
                image_url = self.image_generator.generate_image_for_blink(main_title, superior_note_content[:500])
            except Exception as e:
                print(f"[SuperiorNoteGenerator] ERROR: ImageGenerator failed: {e}")
                # image_url remains None
        else:
            print("[SuperiorNoteGenerator] ImageGenerator not available. Skipping image generation for superior note.")
        
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
            
            # Si no se encuentra contenido específico, usar todo el texto
            if not content:
                content = soup.get_text(separator=' ', strip=True)
            
            # Limpiar el contenido
            content = re.sub(r'\s+', ' ', content)
            content = content[:10000]  # Limitar a 10000 caracteres
            
            # Buscar imagen principal
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
        # Usar el título más representativo o generar uno nuevo
        titles = [content['title'] for content in all_contents]
        
        # Por ahora, usar el título más largo que contenga el tema
        best_title = f"Análisis completo: {topic}"
        
        for title in titles:
            if topic.lower() in title.lower() and len(title) > len(best_title):
                best_title = title
        
        return best_title
    
    def _generate_comprehensive_note(self, all_contents, topic):
        """Genera una nota comprehensiva usando OLLAMA"""
        try:
            # Preparar el contexto para OLLAMA
            context = f"Tema principal: {topic}\n\n"
            context += "Artículos de diferentes fuentes:\n\n"
            
            for i, content in enumerate(all_contents, 1):
                context += f"FUENTE {i} - {content['source']}:\n"
                context += f"Título: {content['title']}\n"
                context += f"Contenido: {content['content'][:2000]}...\n\n"
            
            # Prompt para generar nota superior
            prompt = f"""Basándote en los artículos de múltiples fuentes proporcionados sobre el tema "{topic}", crea una NOTA SUPERIOR comprehensiva que:

1. Integre la información de todas las fuentes
2. Presente múltiples puntos de vista y perspectivas
3. Identifique consensos y discrepancias entre las fuentes
4. Proporcione un análisis equilibrado y completo
5. Mantenga un tono periodístico profesional
6. Tenga una extensión de aproximadamente 800-1200 palabras

La nota debe estar estructurada con:
- Introducción que presente el tema
- Desarrollo que integre las diferentes perspectivas
- Análisis de los puntos clave
- Conclusión que sintetice la información

Contexto de las fuentes:
{context}

NOTA SUPERIOR:"""

            # Llamar a OLLAMA
            response = self.ollama_client.chat(model=self.ollama_model, messages=[
                {
                    'role': 'user',
                    'content': prompt
                }
            ])
            
            return response['message']['content']
            
        except Exception as e:
            print(f"Error generando nota con OLLAMA: {e}")
            # Fallback: generar nota básica
            return self._generate_basic_note(all_contents, topic)
    
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
            
            # Extraer los bullets de la respuesta
            bullets_text = response['message']['content']
            bullets = []
            
            for line in bullets_text.split('\n'):
                line = line.strip()
                if line.startswith('•') or line.startswith('-') or line.startswith('*'):
                    bullet = line[1:].strip()
                    if bullet:
                        bullets.append(bullet)
            
            # Asegurar que tenemos exactamente 5 bullets
            if len(bullets) < 5:
                bullets.extend([f"Punto adicional {i}" for i in range(len(bullets) + 1, 6)])
            elif len(bullets) > 5:
                bullets = bullets[:5]
            
            return bullets
            
        except Exception as e:
            print(f"Error generando ultra resumen con OLLAMA: {e}")
            # Fallback: generar bullets básicos
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
            # Crear directorio si no existe
            notes_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'superior_notes')
            os.makedirs(notes_dir, exist_ok=True)
            
            # Guardar como JSON
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
            
            # Ordenar por timestamp (más recientes primero)
            notes.sort(key=lambda x: x['timestamp'], reverse=True)
            return notes
            
        except Exception as e:
            print(f"Error obteniendo notas superiores: {e}")
            return []

