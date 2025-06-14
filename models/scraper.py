import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta
import hashlib
import os
from difflib import SequenceMatcher

class NewsScraper:
    """Clase para extraer noticias de diferentes fuentes web"""
    
    def __init__(self, config):
        """Inicializa el scraper con configuraciones básicas"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Cargar configuración
        self.sources = config.get('news_sources', [])
        self.default_articles_per_source = config.get('default_articles_per_source', 8)
        self.recency_filter_hours = config.get('recency_filter_hours', 24)
        self.similarity_threshold = config.get('similarity_threshold', 0.6)
    
    def scrape_all_sources(self):
        """Extrae noticias de todas las fuentes configuradas"""
        all_news = []
        
        for source in self.sources:
            try:
                print(f"Extrayendo noticias de {source['name']}...")
                news_items = self.scrape_source(source)
                all_news.extend(news_items)
                # Esperar un poco entre solicitudes para no sobrecargar los servidores
                time.sleep(3)
            except Exception as e:
                print(f"Error al extraer noticias de {source['name']}: {e}")
        
        # Filtrar noticias de las últimas 24 horas
        filtered_news = self.filter_recent_news(all_news)
        
        return filtered_news
    
    def filter_recent_news(self, news_items):
        """Filtra noticias para mostrar solo las de las últimas N horas según configuración"""
        cutoff_time = datetime.now() - timedelta(hours=self.recency_filter_hours)
        recent_news = []
        
        for item in news_items:
            try:
                # Si el timestamp está en formato ISO, convertirlo
                if 'timestamp' in item:
                    item_time = datetime.fromisoformat(item['timestamp'].replace('Z', '+00:00'))
                    if item_time.replace(tzinfo=None) >= cutoff_time:
                        recent_news.append(item)
                else:
                    # Si no hay timestamp, asumir que es reciente
                    recent_news.append(item)
            except Exception as e:
                print(f"Error al filtrar noticia por fecha: {e}")
                # En caso de error, incluir la noticia
                recent_news.append(item)
        
        return recent_news
    
    def scrape_source(self, source):
        """Extrae noticias de una fuente específica"""
        try:
            response = requests.get(source['url'], headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            articles = soup.select(source['article_selector'])
            
            news_items = []
            for article in articles[:self.default_articles_per_source]:
                try:
                    title_element = article.select_one(source['title_selector'])
                    link_element = article.select_one(source['link_selector'])
                    summary_element = article.select_one(source['summary_selector'])
                    
                    if title_element and link_element:
                        title = title_element.get_text().strip()
                        
                        # Manejar URLs relativas
                        link = link_element.get('href')
                        if link and not link.startswith(('http://', 'https://')):
                            if link.startswith('/'):
                                base_url = '/'.join(source['url'].split('/')[:3])
                                link = base_url + link
                            else:
                                link = source['url'].rstrip('/') + '/' + link
                        
                        summary = ""
                        if summary_element:
                            summary = summary_element.get_text().strip()
                        
                        # Validar que el título tenga contenido significativo
                        if title and link and len(title) > 10:
                            # Generar un ID único basado en el título y la URL
                            unique_id = hashlib.md5(f"{title}:{link}".encode()).hexdigest()
                            
                            news_items.append({
                                'id': unique_id,
                                'title': title,
                                'url': link,
                                'summary': summary,
                                'source': source['name'],
                                'category': source['category'],
                                'timestamp': datetime.now().isoformat()
                            })
                except Exception as e:
                    print(f"Error al procesar artículo de {source['name']}: {e}")
                    continue
            
            print(f"Extraídos {len(news_items)} artículos de {source['name']}")
            return news_items
        except Exception as e:
            print(f"Error al extraer noticias de {source['name']}: {e}")
            return []
    
    def get_article_content(self, url):
        """Obtiene el contenido completo de un artículo desde su URL"""
        try:
            response = requests.get(url, headers=self.headers, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Eliminar elementos no deseados
            for element in soup.find_all(['script', 'style', 'nav', 'footer', 'header', 'aside']):
                element.decompose()
            
            # Extraer el contenido principal (esto puede variar según el sitio)
            content = ""
            
            # Intentar diferentes selectores para el contenido principal
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
                content = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 20])
            
            # Intentar extraer una imagen principal
            image_url = None
            
            # Buscar meta tags de Open Graph o Twitter
            meta_tags = [
                soup.find('meta', property='og:image'),
                soup.find('meta', attrs={'name': 'twitter:image'}),
                soup.find('meta', attrs={'property': 'twitter:image'})
            ]
            
            for tag in meta_tags:
                if tag and tag.get('content'):
                    image_url = tag.get('content')
                    break
            
            # Si no se encontró en meta tags, buscar en el contenido
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
    
    def find_similar_news(self, news_items, threshold=None):
        """Agrupa noticias similares basadas en títulos similares con algoritmo mejorado"""
        
        current_threshold = threshold if threshold is not None else self.similarity_threshold

        def similarity(a, b):
            """Calcula la similitud entre dos títulos"""
            return SequenceMatcher(None, a.lower(), b.lower()).ratio()
        
        def extract_keywords(title):
            """Extrae palabras clave de un título"""
            # Palabras comunes a ignorar
            stop_words = {
                'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'por', 'para', 'que', 'se', 'es', 'y', 'o',
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are'
            }
            
            words = re.findall(r'\b\w+\b', title.lower())
            return [word for word in words if len(word) > 2 and word not in stop_words]
        
        def keyword_similarity(title1, title2):
            """Calcula similitud basada en palabras clave comunes"""
            keywords1 = set(extract_keywords(title1))
            keywords2 = set(extract_keywords(title2))
            
            if not keywords1 or not keywords2:
                return 0
            
            intersection = keywords1.intersection(keywords2)
            union = keywords1.union(keywords2)
            
            return len(intersection) / len(union) if union else 0
        
        grouped_news = []
        processed = set()
        
        for i, item in enumerate(news_items):
            if i in processed:
                continue
                
            similar_items = [item]
            processed.add(i)
            
            for j, other_item in enumerate(news_items):
                if j != i and j not in processed:
                    # Calcular similitud textual y por palabras clave
                    text_sim = similarity(item['title'], other_item['title'])
                    keyword_sim = keyword_similarity(item['title'], other_item['title'])
                    
                    # Combinar ambas métricas
                    combined_sim = (text_sim * 0.6) + (keyword_sim * 0.4)
                    
                    if combined_sim > current_threshold:
                        similar_items.append(other_item)
                        processed.add(j)
            
            if similar_items:
                grouped_news.append(similar_items)
        
        print(f"Agrupadas {len(news_items)} noticias en {len(grouped_news)} grupos")
        return grouped_news
