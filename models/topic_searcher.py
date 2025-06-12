import requests
from bs4 import BeautifulSoup
import re
import time
from datetime import datetime, timedelta
import hashlib
import os
from difflib import SequenceMatcher

class TopicSearcher:
    """Clase para buscar noticias por tema específico en múltiples fuentes"""
    
    def __init__(self):
        """Inicializa el buscador de temas"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fuentes de noticias generales (no solo tecnología)
        self.news_sources = [
            # Fuentes argentinas
            {
                'name': 'Clarín',
                'search_url': 'https://www.clarin.com/buscar/?query={topic}',
                'article_selector': '.article-item',
                'title_selector': 'h2 a, h3 a',
                'link_selector': 'h2 a, h3 a',
                'summary_selector': '.article-summary, .bajada',
                'date_selector': '.date, time',
                'country': 'argentina'
            },
            {
                'name': 'La Nación',
                'search_url': 'https://www.lanacion.com.ar/buscar/{topic}',
                'article_selector': '.mod-article',
                'title_selector': 'h2 a, h3 a',
                'link_selector': 'h2 a, h3 a',
                'summary_selector': '.article-summary',
                'date_selector': '.date',
                'country': 'argentina'
            },
            {
                'name': 'Infobae',
                'search_url': 'https://www.infobae.com/buscar/?q={topic}',
                'article_selector': '.story-card',
                'title_selector': 'h2 a, h3 a',
                'link_selector': 'h2 a, h3 a',
                'summary_selector': '.story-summary',
                'date_selector': '.date',
                'country': 'argentina'
            },
            {
                'name': 'Página/12',
                'search_url': 'https://www.pagina12.com.ar/buscar?q={topic}',
                'article_selector': '.article-item',
                'title_selector': 'h2 a, h3 a',
                'link_selector': 'h2 a, h3 a',
                'summary_selector': '.summary',
                'date_selector': '.date',
                'country': 'argentina'
            },
            # Fuentes internacionales en español
            {
                'name': 'El País',
                'search_url': 'https://elpais.com/buscar/?q={topic}',
                'article_selector': 'article',
                'title_selector': 'h2 a, h1 a',
                'link_selector': 'h2 a, h1 a',
                'summary_selector': 'p',
                'date_selector': '.date, time',
                'country': 'españa'
            },
            {
                'name': 'BBC Mundo',
                'search_url': 'https://www.bbc.com/mundo/search?q={topic}',
                'article_selector': '.search-result',
                'title_selector': 'h3 a',
                'link_selector': 'h3 a',
                'summary_selector': '.search-result-summary',
                'date_selector': '.date',
                'country': 'internacional'
            }
        ]
    
    def search_topic_news(self, topic, hours_back=24, max_sources=5):
        """
        Busca noticias sobre un tema específico en las últimas horas
        
        Args:
            topic (str): Tema a buscar (ej: "Argentina", "elecciones", etc.)
            hours_back (int): Horas hacia atrás para buscar (default: 24)
            max_sources (int): Máximo número de fuentes a consultar
            
        Returns:
            list: Lista de noticias encontradas agrupadas por evento
        """
        print(f"Buscando noticias sobre '{topic}' en las últimas {hours_back} horas...")
        
        all_news = []
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        # Buscar en cada fuente
        for source in self.news_sources[:max_sources]:
            try:
                print(f"Buscando en {source['name']}...")
                news_from_source = self._search_in_source(source, topic, cutoff_time)
                all_news.extend(news_from_source)
                time.sleep(1)  # Pausa entre requests
            except Exception as e:
                print(f"Error buscando en {source['name']}: {e}")
                continue
        
        # Agrupar noticias similares
        grouped_news = self._group_similar_news(all_news)
        
        # Filtrar grupos con al menos 2 fuentes
        filtered_groups = [group for group in grouped_news if len(group) >= 2]
        
        print(f"Encontrados {len(filtered_groups)} eventos con múltiples fuentes")
        return filtered_groups
    
    def _search_in_source(self, source, topic, cutoff_time):
        """Busca noticias en una fuente específica"""
        try:
            # Construir URL de búsqueda
            search_url = source['search_url'].format(topic=topic.replace(' ', '+'))
            
            response = requests.get(search_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.select(source['article_selector'])
            
            news_items = []
            
            for article in articles[:10]:  # Limitar a 10 artículos por fuente
                try:
                    # Extraer título
                    title_elem = article.select_one(source['title_selector'])
                    if not title_elem:
                        continue
                    
                    title = title_elem.get_text(strip=True)
                    
                    # Extraer enlace
                    link_elem = article.select_one(source['link_selector'])
                    if not link_elem:
                        continue
                    
                    link = link_elem.get('href', '')
                    if link.startswith('/'):
                        # URL relativa, convertir a absoluta
                        base_url = f"https://{requests.utils.urlparse(search_url).netloc}"
                        link = base_url + link
                    
                    # Extraer resumen
                    summary_elem = article.select_one(source['summary_selector'])
                    summary = summary_elem.get_text(strip=True) if summary_elem else ""
                    
                    # Extraer fecha (simplificado - en implementación real sería más complejo)
                    date_elem = article.select_one(source.get('date_selector', ''))
                    article_date = datetime.now()  # Por ahora usar fecha actual
                    
                    # Verificar si la noticia es reciente
                    if article_date >= cutoff_time:
                        news_item = {
                            'title': title,
                            'url': link,
                            'summary': summary,
                            'source': source['name'],
                            'country': source.get('country', 'unknown'),
                            'timestamp': article_date.isoformat(),
                            'topic': topic
                        }
                        news_items.append(news_item)
                
                except Exception as e:
                    print(f"Error procesando artículo en {source['name']}: {e}")
                    continue
            
            return news_items
            
        except Exception as e:
            print(f"Error accediendo a {source['name']}: {e}")
            return []
    
    def _group_similar_news(self, news_list):
        """Agrupa noticias similares basándose en el título y contenido"""
        if not news_list:
            return []
        
        groups = []
        used_indices = set()
        
        for i, news1 in enumerate(news_list):
            if i in used_indices:
                continue
            
            # Crear nuevo grupo con esta noticia
            current_group = [news1]
            used_indices.add(i)
            
            # Buscar noticias similares
            for j, news2 in enumerate(news_list):
                if j in used_indices or i == j:
                    continue
                
                # Calcular similitud entre títulos
                similarity = self._calculate_similarity(news1['title'], news2['title'])
                
                # Si son similares, agregar al grupo
                if similarity > 0.6:  # Umbral de similitud
                    current_group.append(news2)
                    used_indices.add(j)
            
            # Solo agregar grupos con al menos 2 noticias
            if len(current_group) >= 2:
                groups.append(current_group)
        
        return groups
    
    def _calculate_similarity(self, text1, text2):
        """Calcula la similitud entre dos textos"""
        # Normalizar textos
        text1 = re.sub(r'[^\w\s]', '', text1.lower())
        text2 = re.sub(r'[^\w\s]', '', text2.lower())
        
        # Usar SequenceMatcher para calcular similitud
        return SequenceMatcher(None, text1, text2).ratio()
    
    def find_related_articles(self, main_article, max_articles=5):
        """
        Encuentra artículos relacionados a un artículo principal
        
        Args:
            main_article (dict): Artículo principal
            max_articles (int): Máximo número de artículos relacionados
            
        Returns:
            list: Lista de artículos relacionados
        """
        # Extraer palabras clave del título principal
        keywords = self._extract_keywords(main_article['title'])
        
        related_articles = []
        
        # Buscar en cada fuente usando las palabras clave
        for source in self.news_sources[:max_articles]:
            try:
                # Buscar usando las palabras clave
                search_query = ' '.join(keywords[:3])  # Usar las 3 palabras más importantes
                articles = self._search_in_source(source, search_query, datetime.now() - timedelta(hours=48))
                
                # Filtrar artículos similares al principal
                for article in articles:
                    similarity = self._calculate_similarity(main_article['title'], article['title'])
                    if 0.4 < similarity < 0.9:  # Similar pero no idéntico
                        related_articles.append(article)
                        break  # Solo uno por fuente
                        
            except Exception as e:
                print(f"Error buscando artículos relacionados en {source['name']}: {e}")
                continue
        
        return related_articles[:max_articles]
    
    def _extract_keywords(self, text):
        """Extrae palabras clave de un texto"""
        # Palabras comunes a ignorar
        stop_words = {'el', 'la', 'de', 'que', 'y', 'a', 'en', 'un', 'es', 'se', 'no', 'te', 'lo', 'le', 'da', 'su', 'por', 'son', 'con', 'para', 'al', 'del', 'los', 'las', 'una', 'como', 'pero', 'sus', 'han', 'fue', 'ser', 'está', 'más', 'este', 'esta', 'sobre', 'todo', 'muy', 'sin', 'hasta', 'entre', 'cuando', 'desde', 'donde', 'dos', 'tres', 'años', 'año', 'día', 'días'}
        
        # Limpiar y dividir el texto
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filtrar palabras comunes y cortas
        keywords = [word for word in words if word not in stop_words and len(word) > 3]
        
        # Ordenar por frecuencia (en implementación real usaríamos TF-IDF)
        return keywords

