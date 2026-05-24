import json
import logging
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_driver():
    """Inicializa Chrome headless con waits implícitos"""
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(10)
    return driver

def scrape_bbva():
    """Raspa de https://bbva.com.ar/beneficios/beneficios"""
    logger.info("🔄 Scrapeando BBVA...")
    descuentos = []
    driver = None
    
    try:
        driver = init_driver()
        url = "https://www.bbva.com.ar/beneficios/beneficios"
        driver.get(url)
        
        # Esperar a que cargue el contenido principal
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "h2")))
        
        # Hacer scroll múltiple para cargar todo
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 500)")
            time.sleep(1)
        
        # Buscar todos los divs/articles que contengan texto con %
        elementos = driver.find_elements(By.XPATH, "//*[contains(text(), '%')]")
        logger.info(f"  Encontrados {len(elementos)} elementos con %")
        
        # Obtener todo el texto de la página
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lineas = page_text.split("\n")
        
        comercios_encontrados = set()
        for i, linea in enumerate(lineas):
            if "%" in linea and len(linea) < 100:
                # Extraer %
                porcentaje = None
                try:
                    for palabra in linea.split():
                        if "%" in palabra:
                            porcentaje = int(palabra.replace("%", "").strip())
                            break
                except:
                    continue
                
                if porcentaje and 0 < porcentaje <= 100:
                    # Buscar el comercio en líneas anteriores
                    comercio = "BBVA"
                    for j in range(max(0, i-5), i):
                        if lineas[j].strip() and len(lineas[j]) < 50:
                            if any(palabra in lineas[j].upper() for palabra in ["NIKE", "PUPPIS", "COTO", "CARREFOUR", "JUMBO", "RESTAURANTE", "FARMA", "ELECTRO", "ROPA"]):
                                comercio = lineas[j].strip()
                                break
                    
                    key = f"BBVA_{comercio}_{porcentaje}"
                    if key not in comercios_encontrados:
                        comercios_encontrados.add(key)
                        descuentos.append({
                            "banco": "BBVA",
                            "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg",
                            "metodo": "TC Visa",
                            "marca": "Visa",
                            "comercio": comercio,
                            "categoria": "Múltiple",
                            "porcentaje": porcentaje,
                            "tope": 12000,
                            "dias": ["todos"],
                            "link": url
                        })
    
    except Exception as e:
        logger.error(f"Error BBVA: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return descuentos

def scrape_galicia():
    """Raspa de https://beneficios.galicia.ar/"""
    logger.info("🔄 Scrapeando Galicia...")
    descuentos = []
    driver = None
    
    try:
        driver = init_driver()
        url = "https://beneficios.galicia.ar/"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        
        # Scroll para cargar todo
        for _ in range(8):
            driver.execute_script("window.scrollBy(0, 1000)")
            time.sleep(1)
        
        # Obtener texto de página
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lineas = page_text.split("\n")
        
        comercios_encontrados = set()
        for i, linea in enumerate(lineas):
            if "%" in linea and "reintegro" in linea.lower():
                porcentaje = None
                try:
                    for palabra in linea.split():
                        if "%" in palabra:
                            porcentaje = int(palabra.replace("%", "").strip())
                            break
                except:
                    continue
                
                if porcentaje and 0 < porcentaje <= 100:
                    comercio = "Galicia"
                    for j in range(max(0, i-3), i):
                        if lineas[j].strip() and len(lineas[j]) < 50:
                            if any(palabra in lineas[j].upper() for palabra in ["COTO", "CARREFOUR", "JUMBO", "DÍA", "VEA", "CHANGO", "FARMA", "RESTAURANTE", "ARREDO", "COTO DIGITAL"]):
                                comercio = lineas[j].strip()
                                break
                    
                    key = f"Galicia_{comercio}_{porcentaje}"
                    if key not in comercios_encontrados:
                        comercios_encontrados.add(key)
                        descuentos.append({
                            "banco": "Banco Galicia",
                            "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg",
                            "metodo": "TC Visa",
                            "marca": "Visa",
                            "comercio": comercio,
                            "categoria": "Múltiple",
                            "porcentaje": porcentaje,
                            "tope": 15000,
                            "dias": ["todos"],
                            "link": url
                        })
    
    except Exception as e:
        logger.error(f"Error Galicia: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return descuentos

def scrape_santander():
    """Raspa de https://www.santander.com.ar/personas/beneficios"""
    logger.info("🔄 Scrapeando Santander...")
    descuentos = []
    driver = None
    
    try:
        driver = init_driver()
        url = "https://www.santander.com.ar/personas/beneficios"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        
        for _ in range(8):
            driver.execute_script("window.scrollBy(0, 1000)")
            time.sleep(1)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lineas = page_text.split("\n")
        
        comercios_encontrados = set()
        for i, linea in enumerate(lineas):
            if "%" in linea and len(linea) < 100:
                porcentaje = None
                try:
                    for palabra in linea.split():
                        if "%" in palabra:
                            porcentaje = int(palabra.replace("%", "").strip())
                            break
                except:
                    continue
                
                if porcentaje and 0 < porcentaje <= 100:
                    comercio = "Santander"
                    for j in range(max(0, i-3), i):
                        if lineas[j].strip() and len(lineas[j]) < 50:
                            if any(palabra in lineas[j].upper() for palabra in ["COTO", "CARREFOUR", "DISCO", "VEA", "JUMBO", "ROPA", "GASTRONOMÍA", "Nike", "DECATHLON"]):
                                comercio = lineas[j].strip()
                                break
                    
                    key = f"Santander_{comercio}_{porcentaje}"
                    if key not in comercios_encontrados:
                        comercios_encontrados.add(key)
                        descuentos.append({
                            "banco": "Santander",
                            "logo": "https://cdn.worldvectorlogo.com/logos/santander.svg",
                            "metodo": "TC Visa",
                            "marca": "Visa",
                            "comercio": comercio,
                            "categoria": "Múltiple",
                            "porcentaje": porcentaje,
                            "tope": 10000,
                            "dias": ["todos"],
                            "link": url
                        })
    
    except Exception as e:
        logger.error(f"Error Santander: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return descuentos

def scrape_itau():
    """Raspa de https://www.itau.com.ar/beneficios"""
    logger.info("🔄 Scrapeando Itaú...")
    descuentos = []
    driver = None
    
    try:
        driver = init_driver()
        url = "https://www.itau.com.ar/beneficios"
        driver.get(url)
        
        wait = WebDriverWait(driver, 15)
        wait.until(EC.presence_of_all_elements_located((By.TAG_NAME, "body")))
        
        for _ in range(5):
            driver.execute_script("window.scrollBy(0, 800)")
            time.sleep(1)
        
        page_text = driver.find_element(By.TAG_NAME, "body").text
        lineas = page_text.split("\n")
        
        comercios_encontrados = set()
        for i, linea in enumerate(lineas):
            if "%" in linea and len(linea) < 100:
                porcentaje = None
                try:
                    for palabra in linea.split():
                        if "%" in palabra:
                            porcentaje = int(palabra.replace("%", "").strip())
                            break
                except:
                    continue
                
                if porcentaje and 0 < porcentaje <= 100:
                    comercio = "Itaú"
                    key = f"Itau_{comercio}_{porcentaje}"
                    if key not in comercios_encontrados:
                        comercios_encontrados.add(key)
                        descuentos.append({
                            "banco": "Itaú",
                            "logo": "https://cdn.worldvectorlogo.com/logos/itau-2.svg",
                            "metodo": "TC Visa",
                            "marca": "Visa",
                            "comercio": comercio,
                            "categoria": "Múltiple",
                            "porcentaje": porcentaje,
                            "tope": 6000,
                            "dias": ["todos"],
                            "link": url
                        })
    
    except Exception as e:
        logger.error(f"Error Itaú: {e}")
    
    finally:
        if driver:
            driver.quit()
    
    return descuentos

def scrape_todos_bancos():
    """Raspa de TODOS los bancos oficiales"""
    logger.info("=" * 70)
    logger.info("SCRAPER OFICIAL - PÁGINAS DE BANCOS")
    logger.info("=" * 70)
    
    descuentos_totales = []
    
    descuentos_totales.extend(scrape_bbva())
    descuentos_totales.extend(scrape_galicia())
    descuentos_totales.extend(scrape_santander())
    descuentos_totales.extend(scrape_itau())
    
    logger.info(f"✓ Total obtenido del scraping: {len(descuentos_totales)}")
    
    return descuentos_totales

def format_descuentos(descuentos_data):
    """Convierte a JSON final"""
    descuentos = []
    id_counter = 1
    
    for d in descuentos_data:
        dias = d.get("dias", ["todos"])
        if dias == ["todos"]:
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        
        metodo = d["metodo"].replace("TC ", "Tarjeta de Crédito").replace("TD ", "Tarjeta de Débito").replace("BV ", "Billetera Virtual")
        
        descuentos.append({
            "id": id_counter,
            "banco": d["banco"],
            "logo_url": d["logo"],
            "metodo_pago": metodo,
            "tarjeta_marca": d.get("marca"),
            "comercio": d["comercio"],
            "categoria": d["categoria"],
            "porcentaje": d["porcentaje"],
            "tope_reintegro": d["tope"],
            "dias_vigencia": dias,
            "fecha_inicio": (datetime.now() - timedelta(days=5)).strftime("%Y-%m-%d"),
            "fecha_fin": (datetime.now() + timedelta(days=60)).strftime("%Y-%m-%d"),
            "link_detalle": d["link"],
            "ultima_actualizacion": datetime.now().isoformat() + "Z"
        })
        id_counter += 1
    
    return descuentos

def guardar_json(descuentos):
    """Guarda en data.json"""
    
    # Deduplicar
    descuentos_unicos = []
    vistos = set()
    
    for d in descuentos:
        key = f"{d['banco']}_{d['comercio']}_{d['porcentaje']}"
        if key not in vistos:
            vistos.add(key)
            descuentos_unicos.append(d)
    
    # Ordenar por %
    descuentos_ordenados = sorted(descuentos_unicos, key=lambda x: x['porcentaje'], reverse=True)
    
    # Re-ID
    for idx, d in enumerate(descuentos_ordenados, 1):
        d['id'] = idx
    
    data = {
        "descuentos": descuentos_ordenados,
        "total": len(descuentos_ordenados),
        "ultima_sincronizacion": datetime.now().isoformat() + "Z",
        "fuentes": ["Páginas oficiales de bancos", "Selenium + React", "Mayo 2026"]
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ {len(descuentos_ordenados)} descuentos guardados")

if __name__ == "__main__":
    descuentos = scrape_todos_bancos()
    descuentos_formateados = format_descuentos(descuentos)
    guardar_json(descuentos_formateados)
    logger.info("=" * 70)
    logger.info("✓ COMPLETADO")
    logger.info("=" * 70)
