import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Este script raspa promociones bancarias de Argentina
# Se ejecuta automáticamente cada día a las 3am vía GitHub Actions

def scrape_descuentos():
    """
    Raspa descuentos de MODO (hub de promociones bancarias argentinas)
    y otros portales de bancos
    """
    
    descuentos = []
    
    # FUENTE 1: MODO.COM.AR
    try:
        url = "https://www.modo.com.ar/promos"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Buscar cards de promociones (ajustar selectors según estructura real)
        promos = soup.find_all('div', class_='promo-card')
        
        for idx, promo in enumerate(promos[:20]):  # Limitar a 20 para no saturar
            try:
                banco = promo.find('span', class_='banco-nombre')
                descuento = promo.find('span', class_='porcentaje')
                comercio = promo.find('span', class_='comercio')
                
                if banco and descuento and comercio:
                    descuentos.append({
                        "id": len(descuentos) + 1,
                        "banco": banco.text.strip(),
                        "logo_url": f"https://via.placeholder.com/40?text={banco.text.strip()[:3]}",
                        "metodo_pago": "Tarjeta de Crédito",
                        "tarjeta_marca": "Visa",
                        "comercio": comercio.text.strip(),
                        "categoria": "Supermercado",
                        "porcentaje": int(descuento.text.replace('%', '').strip()),
                        "tope_reintegro": 10000,
                        "dias_vigencia": ["todos"],
                        "fecha_inicio": "2026-05-24",
                        "fecha_fin": "2026-06-30",
                        "link_detalle": "https://www.modo.com.ar/promos",
                        "ultima_actualizacion": datetime.now().isoformat() + "Z"
                    })
            except Exception as e:
                print(f"Error procesando promo: {e}")
                continue
    
    except Exception as e:
        print(f"Error scrapeando MODO: {e}")
    
    # FUENTE 2: OFERTAS DIRECTAS DE BANCOS (placeholders, expandir manualmente)
    descuentos_fijos = [
        {
            "id": len(descuentos) + 1,
            "banco": "BBVA",
            "logo_url": "https://cdn.worldvectorlogo.com/logos/bbva.svg",
            "metodo_pago": "Tarjeta de Crédito",
            "tarjeta_marca": "Visa",
            "comercio": "COTO",
            "categoria": "Supermercado",
            "porcentaje": 25,
            "tope_reintegro": 12000,
            "dias_vigencia": ["lunes"],
            "fecha_inicio": "2026-05-01",
            "fecha_fin": "2026-06-30",
            "link_detalle": "https://www.coto.com.ar/promociones",
            "ultima_actualizacion": datetime.now().isoformat() + "Z"
        },
        {
            "id": len(descuentos) + 2,
            "banco": "Galicia",
            "logo_url": "https://cdn.worldvectorlogo.com/logos/galicia.svg",
            "metodo_pago": "Tarjeta de Débito",
            "tarjeta_marca": "Mastercard",
            "comercio": "Carrefour",
            "categoria": "Supermercado",
            "porcentaje": 15,
            "tope_reintegro": 10000,
            "dias_vigencia": ["martes"],
            "fecha_inicio": "2026-05-15",
            "fecha_fin": "2026-06-30",
            "link_detalle": "https://www.carrefour.com.ar/promociones",
            "ultima_actualizacion": datetime.now().isoformat() + "Z"
        }
    ]
    
    descuentos.extend(descuentos_fijos)
    
    return descuentos

def guardar_json(descuentos):
    """Guarda los descuentos en data.json"""
    data = {
        "descuentos": descuentos,
        "ultima_sincronizacion": datetime.now().isoformat() + "Z"
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"✓ {len(descuentos)} descuentos guardados en data.json")

if __name__ == "__main__":
    print("🔄 Iniciando scraping de descuentos bancarios...")
    descuentos = scrape_descuentos()
    guardar_json(descuentos)
    print("✓ Completado")
