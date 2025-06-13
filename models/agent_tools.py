# models/agent_tools.py

from langchain.tools import tool
from duckduckgo_search import DDGS
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import re
import time

@tool
def buscar_en_la_web(query: str) -> str:
    """
    Realiza una búsqueda web y devuelve los 5 mejores resultados.
    Usa esta herramienta para encontrar URLs de noticias relevantes sobre un tema.
    """
    print(f"🤖 Usando herramienta de búsqueda para: '{query}'")
    try:
        with DDGS() as ddgs:
            resultados = [r for r in ddgs.text(query, max_results=5)]
        if not resultados:
            return "No se encontraron resultados para la búsqueda."
        return "\n".join([
            f"Título: {res['title']}\nURL: {res['href']}\nResumen: {res['body']}\n---"
            for res in resultados
        ])
    except Exception as e:
        return f"Error durante la búsqueda web: {e}"

@tool
def leer_contenido_web(url: str) -> str:
    """
    Lee y extrae el contenido textual limpio de una página web a partir de su URL.
    Usa esta herramienta DESPUÉS de haber encontrado una URL con 'buscar_en_la_web'.
    """
    print(f"🤖 Usando herramienta de lectura web para: '{url}'")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)
        driver.get(url)
        time.sleep(3) # Esperar a que el JavaScript cargue
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            element.decompose()

        body_text = soup.body.get_text(separator=' ', strip=True)
        cleaned_text = re.sub(r'\s+', ' ', body_text)

        # Devolvemos solo una porción para no sobrecargar al LLM
        return cleaned_text[:8000]
    except Exception as e:
        return f"Error al leer la URL {url}: {e}"
    finally:
        if driver:
            driver.quit()
