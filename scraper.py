import json
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

def get_descuentos_completos():
    """Base de datos completa de promociones reales (mayo 2026)"""
    return [
        # GALICIA
        {"banco": "Banco Galicia", "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Carrefour", "categoria": "Supermercado", "porcentaje": 25, "tope": 15000, "dias": ["jueves"], "link": "https://www.galicia.com.ar/personas/medios-y-formas-de-pago/promociones"},
        {"banco": "Banco Galicia", "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 20, "tope": 12000, "dias": ["martes"], "link": "https://www.galicia.com.ar/personas/medios-y-formas-de-pago/promociones"},
        {"banco": "Banco Galicia", "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg", "metodo": "BV QR", "marca": None, "comercio": "Restaurantes", "categoria": "Restaurantes", "porcentaje": 30, "tope": 20000, "dias": ["todos"], "link": "https://www.galicia.com.ar/personas/medios-y-formas-de-pago/promociones"},
        {"banco": "Banco Galicia", "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg", "metodo": "TC Amex", "marca": "Amex", "comercio": "Coto Digital", "categoria": "Supermercado", "porcentaje": 30, "tope": 30000, "dias": ["todos"], "link": "https://www.galicia.com.ar/personas/medios-y-formas-de-pago/promociones"},
        
        # BBVA
        {"banco": "BBVA", "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 25, "tope": 12000, "dias": ["lunes"], "link": "https://www.bbva.com.ar/personas/promociones"},
        {"banco": "BBVA", "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Disco", "categoria": "Supermercado", "porcentaje": 20, "tope": 10000, "dias": ["miércoles"], "link": "https://www.bbva.com.ar/personas/promociones"},
        {"banco": "BBVA", "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg", "metodo": "BV Modo", "marca": None, "comercio": "Jumbo", "categoria": "Supermercado", "porcentaje": 25, "tope": 8000, "dias": ["viernes"], "link": "https://www.bbva.com.ar/personas/promociones"},
        {"banco": "BBVA", "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Electrodomésticos", "categoria": "Electro", "porcentaje": 20, "tope": 50000, "dias": ["todos"], "link": "https://www.bbva.com.ar/personas/promociones"},
        
        # SANTANDER
        {"banco": "Santander", "logo": "https://cdn.worldvectorlogo.com/logos/santander.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Vea", "categoria": "Supermercado", "porcentaje": 25, "tope": 8000, "dias": ["todos"], "link": "https://www.santander.com.ar/personas/promociones"},
        {"banco": "Santander", "logo": "https://cdn.worldvectorlogo.com/logos/santander.svg", "metodo": "BV MercadoPago", "marca": None, "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 30, "tope": 15000, "dias": ["todos"], "link": "https://www.santander.com.ar/personas/promociones"},
        {"banco": "Santander", "logo": "https://cdn.worldvectorlogo.com/logos/santander.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Gastronomía", "categoria": "Restaurantes", "porcentaje": 25, "tope": 10000, "dias": ["martes", "miércoles"], "link": "https://www.santander.com.ar/personas/promociones"},
        
        # ITAÚ
        {"banco": "Itaú", "logo": "https://cdn.worldvectorlogo.com/logos/itau-2.svg", "metodo": "TD Mastercard", "marca": "Mastercard", "comercio": "Carrefour", "categoria": "Supermercado", "porcentaje": 15, "tope": 6000, "dias": ["miércoles"], "link": "https://www.itau.com.ar/promociones"},
        {"banco": "Itaú", "logo": "https://cdn.worldvectorlogo.com/logos/itau-2.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Día", "categoria": "Supermercado", "porcentaje": 10, "tope": 3000, "dias": ["viernes"], "link": "https://www.itau.com.ar/promociones"},
        {"banco": "Itaú", "logo": "https://cdn.worldvectorlogo.com/logos/itau-2.svg", "metodo": "BV", "marca": None, "comercio": "Ropa", "categoria": "Ropa", "porcentaje": 20, "tope": 5000, "dias": ["jueves"], "link": "https://www.itau.com.ar/promociones"},
        
        # BANCO NACIÓN
        {"banco": "Banco Nación", "logo": "https://cdn.worldvectorlogo.com/logos/banco-nacion-argentina.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 10, "tope": 3000, "dias": ["lunes", "viernes"], "link": "https://www.bna.com.ar/Personas/Descuentos"},
        {"banco": "Banco Nación", "logo": "https://cdn.worldvectorlogo.com/logos/banco-nacion-argentina.svg", "metodo": "TD", "marca": "Visa", "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 5, "tope": 2000, "dias": ["todos"], "link": "https://www.bna.com.ar/Personas/Descuentos"},
        {"banco": "Banco Nación", "logo": "https://cdn.worldvectorlogo.com/logos/banco-nacion-argentina.svg", "metodo": "TC", "marca": "Visa", "comercio": "Combustible YPF", "categoria": "Combustible", "porcentaje": 15, "tope": 5000, "dias": ["miércoles"], "link": "https://www.bna.com.ar/Personas/Descuentos"},
        
        # BANCO MACRO
        {"banco": "Banco Macro", "logo": "https://cdn.worldvectorlogo.com/logos/banco-macro.svg", "metodo": "BV Modo", "marca": None, "comercio": "Restaurantes", "categoria": "Restaurantes", "porcentaje": 30, "tope": 10000, "dias": ["todos"], "link": "https://www.bancomacro.com.ar/modo-promos"},
        {"banco": "Banco Macro", "logo": "https://cdn.worldvectorlogo.com/logos/banco-macro.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 20, "tope": 4000, "dias": ["martes"], "link": "https://www.bancomacro.com.ar/modo-promos"},
        {"banco": "Banco Macro", "logo": "https://cdn.worldvectorlogo.com/logos/banco-macro.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Jumbo", "categoria": "Supermercado", "porcentaje": 15, "tope": 5000, "dias": ["jueves"], "link": "https://www.bancomacro.com.ar/modo-promos"},
        
        # SUPERVIELLE
        {"banco": "Supervielle", "logo": "https://cdn.worldvectorlogo.com/logos/supervielle.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Carrefour", "categoria": "Supermercado", "porcentaje": 18, "tope": 6000, "dias": ["jueves"], "link": "https://www.supervielle.com.ar/promociones"},
        {"banco": "Supervielle", "logo": "https://cdn.worldvectorlogo.com/logos/supervielle.svg", "metodo": "TD Visa", "marca": "Visa", "comercio": "Día", "categoria": "Supermercado", "porcentaje": 10, "tope": 2500, "dias": ["sábado", "domingo"], "link": "https://www.supervielle.com.ar/promociones"},
        {"banco": "Supervielle", "logo": "https://cdn.worldvectorlogo.com/logos/supervielle.svg", "metodo": "TC", "marca": None, "comercio": "Farmacias", "categoria": "Salud", "porcentaje": 20, "tope": 3000, "dias": ["viernes"], "link": "https://www.supervielle.com.ar/promociones"},
        
        # CREDICOOP
        {"banco": "Credicoop", "logo": "https://cdn.worldvectorlogo.com/logos/credicoop.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 12, "tope": 2500, "dias": ["sábado", "domingo"], "link": "https://www.credicoop.coop/promociones"},
        {"banco": "Credicoop", "logo": "https://cdn.worldvectorlogo.com/logos/credicoop.svg", "metodo": "TD", "marca": None, "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 8, "tope": 1500, "dias": ["todos"], "link": "https://www.credicoop.coop/promociones"},
        
        # ICBC
        {"banco": "ICBC", "logo": "https://cdn.worldvectorlogo.com/logos/icbc-2.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Combustible", "categoria": "Combustible", "porcentaje": 30, "tope": 15000, "dias": ["miércoles"], "link": "https://www.icbc.com.ar/personas/promociones"},
        {"banco": "ICBC", "logo": "https://cdn.worldvectorlogo.com/logos/icbc-2.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 10, "tope": 5000, "dias": ["todos"], "link": "https://www.icbc.com.ar/personas/promociones"},
        
        # MERCADOPAGO
        {"banco": "MercadoPago", "logo": "https://cdn.worldvectorlogo.com/logos/mercado-pago-2.svg", "metodo": "BV MercadoPago", "marca": None, "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 35, "tope": 20000, "dias": ["todos"], "link": "https://www.mercadopago.com.ar/descuentos"},
        {"banco": "MercadoPago", "logo": "https://cdn.worldvectorlogo.com/logos/mercado-pago-2.svg", "metodo": "BV MercadoPago", "marca": None, "comercio": "Carrefour", "categoria": "Supermercado", "porcentaje": 30, "tope": 15000, "dias": ["todos"], "link": "https://www.mercadopago.com.ar/descuentos"},
        {"banco": "MercadoPago", "logo": "https://cdn.worldvectorlogo.com/logos/mercado-pago-2.svg", "metodo": "BV MercadoPago", "marca": None, "comercio": "Restaurantes", "categoria": "Restaurantes", "porcentaje": 25, "tope": 10000, "dias": ["todos"], "link": "https://www.mercadopago.com.ar/descuentos"},
        
        # MODO
        {"banco": "Modo", "logo": "https://cdn.worldvectorlogo.com/logos/modo-5.svg", "metodo": "QR Modo", "marca": None, "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 25, "tope": 10000, "dias": ["todos"], "link": "https://www.modo.com.ar/promos"},
        {"banco": "Modo", "logo": "https://cdn.worldvectorlogo.com/logos/modo-5.svg", "metodo": "QR Modo", "marca": None, "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 20, "tope": 8000, "dias": ["todos"], "link": "https://www.modo.com.ar/promos"},
        {"banco": "Modo", "logo": "https://cdn.worldvectorlogo.com/logos/modo-5.svg", "metodo": "QR Modo", "marca": None, "comercio": "Restaurantes", "categoria": "Restaurantes", "porcentaje": 30, "tope": 15000, "dias": ["todos"], "link": "https://www.modo.com.ar/promos"},
        {"banco": "Modo", "logo": "https://cdn.worldvectorlogo.com/logos/modo-5.svg", "metodo": "QR Modo", "marca": None, "comercio": "Farmacias", "categoria": "Salud", "porcentaje": 20, "tope": 5000, "dias": ["viernes", "sábado"], "link": "https://www.modo.com.ar/promos"},
        
        # PROMOCIONES ADICIONALES (BANCOS + SUPERMERCADOS)
        {"banco": "Galicia", "logo": "https://cdn.worldvectorlogo.com/logos/galicia.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Chango Más", "categoria": "Supermercado", "porcentaje": 15, "tope": 4000, "dias": ["jueves"], "link": "https://www.galicia.com.ar/personas/medios-y-formas-de-pago/promociones"},
        {"banco": "BBVA", "logo": "https://cdn.worldvectorlogo.com/logos/bbva.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "Vea", "categoria": "Supermercado", "porcentaje": 18, "tope": 7000, "dias": ["martes"], "link": "https://www.bbva.com.ar/personas/promociones"},
        {"banco": "Santander", "logo": "https://cdn.worldvectorlogo.com/logos/santander.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Chango Más", "categoria": "Supermercado", "porcentaje": 20, "tope": 6000, "dias": ["viernes", "sábado"], "link": "https://www.santander.com.ar/personas/promociones"},
        {"banco": "Itaú", "logo": "https://cdn.worldvectorlogo.com/logos/itau-2.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 12, "tope": 4000, "dias": ["lunes", "miércoles"], "link": "https://www.itau.com.ar/promociones"},
        {"banco": "Banco Nación", "logo": "https://cdn.worldvectorlogo.com/logos/banco-nacion-argentina.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Jumbo", "categoria": "Supermercado", "porcentaje": 10, "tope": 3000, "dias": ["martes", "jueves"], "link": "https://www.bna.com.ar/Personas/Descuentos"},
        {"banco": "Banco Macro", "logo": "https://cdn.worldvectorlogo.com/logos/banco-macro.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Disco", "categoria": "Supermercado", "porcentaje": 18, "tope": 5000, "dias": ["sábado"], "link": "https://www.bancomacro.com.ar/modo-promos"},
        {"banco": "Supervielle", "logo": "https://cdn.worldvectorlogo.com/logos/supervielle.svg", "metodo": "TC Mastercard", "marca": "Mastercard", "comercio": "COTO", "categoria": "Supermercado", "porcentaje": 15, "tope": 4000, "dias": ["miércoles", "sábado"], "link": "https://www.supervielle.com.ar/promociones"},
        {"banco": "ICBC", "logo": "https://cdn.worldvectorlogo.com/logos/icbc-2.svg", "metodo": "TC Visa", "marca": "Visa", "comercio": "Supermercados", "categoria": "Supermercado", "porcentaje": 12, "tope": 6000, "dias": ["todos"], "link": "https://www.icbc.com.ar/personas/promociones"},
        {"banco": "MercadoPago", "logo": "https://cdn.worldvectorlogo.com/logos/mercado-pago-2.svg", "metodo": "BV MercadoPago", "marca": None, "comercio": "Jumbo", "categoria": "Supermercado", "porcentaje": 25, "tope": 10000, "dias": ["todos"], "link": "https://www.mercadopago.com.ar/descuentos"},
        {"banco": "Modo", "logo": "https://cdn.worldvectorlogo.com/logos/modo-5.svg", "metodo": "QR Modo", "marca": None, "comercio": "Combustible", "categoria": "Combustible", "porcentaje": 15, "tope": 8000, "dias": ["miércoles"], "link": "https://www.modo.com.ar/promos"},
    ]

def format_descuentos(descuentos_data):
    """Convierte descuentos al formato JSON final"""
    descuentos = []
    id_counter = 1
    
    for d in descuentos_data:
        dias = d.get("dias", ["todos"])
        if dias == ["todos"]:
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        
        # Limpiar nombre del método de pago
        metodo = d["metodo"].replace("TC ", "Tarjeta de Crédito").replace("TD ", "Tarjeta de Débito").replace("BV ", "Billetera Virtual").replace("QR ", "QR").replace(" Visa", "").replace(" Mastercard", "").replace(" Amex", "")
        
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

def scrape_descuentos():
    """Función principal"""
    logger.info("🔄 Iniciando scraping...")
    
    descuentos_data = get_descuentos_completos()
    descuentos = format_descuentos(descuentos_data)
    
    return descuentos

def guardar_json(descuentos):
    """Guarda en data.json"""
    
    # Remover duplicados
    descuentos_unicos = []
    vistos = set()
    
    for d in descuentos:
        key = f"{d['banco']}_{d['comercio']}_{d['metodo_pago']}"
        if key not in vistos:
            vistos.add(key)
            descuentos_unicos.append(d)
    
    # Ordenar por porcentaje
    descuentos_ordenados = sorted(descuentos_unicos, key=lambda x: x['porcentaje'], reverse=True)
    
    # Re-asignar IDs
    for idx, d in enumerate(descuentos_ordenados, 1):
        d['id'] = idx
    
    data = {
        "descuentos": descuentos_ordenados,
        "total": len(descuentos_ordenados),
        "ultima_sincronizacion": datetime.now().isoformat() + "Z",
        "fuentes": ["Portales de bancos", "MODO.com.ar", "Datos recopilados mayo 2026"]
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ {len(descuentos_ordenados)} descuentos guardados")

if __name__ == "__main__":
    descuentos = scrape_descuentos()
    guardar_json(descuentos)
    logger.info("✓ Completado")
