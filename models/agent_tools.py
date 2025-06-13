# models/agent_tools.py

from langchain.tools import tool
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import quote_plus
import tempfile # <-- NUEVO IMPORT para directorios temporales

def get_chrome_options():
    """Crea una configuración de opciones de Chrome robusta y con un perfil único."""
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    # --- LÍNEA CLAVE DE LA SOLUCIÓN ---
    # Crear un directorio de perfil temporal y único para cada instancia del navegador.
    # Esto evita el error "user data directory is already in use".
    user_data_dir = tempfile.mkdtemp()
    chrome_options.add_argument(f"--user-data-dir={user_data_dir}")
    chrome_options.add_argument("--disable-dev-shm-usage") # Mover aquí para mejor orden

    return chrome_options

@tool
def buscar_en_la_web(query: str) -> str:
    """Realiza una búsqueda en Google y devuelve los 5 mejores resultados."""
    print(f"🤖 Usando herramienta de BÚSQUEDA DIRECTA para: '{query}'")
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        wait = WebDriverWait(driver, 10)
        search_query_encoded = quote_plus(query)
        search_url = f"https://www.google.com/search?q={search_query_encoded}"
        print(f"Navegando directamente a: {search_url}")
        driver.get(search_url)
        wait.until(EC.presence_of_element_located((By.ID, "search")))
        soup = BeautifulSoup(driver.page_source, "html.parser")
        results = []
        for result_div in soup.select("div.g"):
            link_tag = result_div.find('a')
            title_tag = result_div.find('h3')
            if link_tag and title_tag and link_tag.get('href'):
                link = link_tag['href']
                title = title_tag.text
                if link.startswith("http") and "google.com" not in link:
                    results.append({"title": title, "href": link})
                    if len(results) >= 5:
                        break
        if not results: return "No se encontraron resultados de búsqueda."
        return "\n".join([f"Título: {res['title']}\nURL: {res['href']}" for res in results])
    except Exception as e:
        return f"Error durante la búsqueda web con Selenium: {e}"
    finally:
        if driver:
            driver.quit()

@tool
def leer_contenido_web(url: str) -> str:
    """Lee y extrae el contenido textual limpio de una página web a partir de su URL."""
    print(f"🤖 Usando herramienta de LECTURA-SELENIUM para: '{url}'")
    driver = None
    try:
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=get_chrome_options())
        driver.get(url)
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        for element in soup(['script', 'style', 'header', 'footer', 'nav', 'aside', 'form', 'button', 'iframe']):
            element.decompose()
        body_text = soup.body.get_text(separator=' ', strip=True)
        cleaned_text = re.sub(r'\s+', ' ', body_text)
        return cleaned_text[:8000] 
    except Exception as e:
        return f"Error al leer la URL {url}: {e}"
    finally:
        if driver:
            driver.quit()