import json
import logging
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def cargar_promociones():
    """Carga promociones.json"""
    with open('promociones.json', 'r', encoding='utf-8') as f:
        return json.load(f)['promociones']

def generar_data_json(promociones):
    """Procesa promociones → data.json"""
    descuentos = []
    
    for idx, promo in enumerate(promociones, 1):
        dias = promo.get("dias_vigencia", ["todos"])
        if "todos" in dias:
            dias = ["lunes", "martes", "miércoles", "jueves", "viernes", "sábado", "domingo"]
        
        descuentos.append({
            "id": idx,
            "banco": promo["banco"],
            "logo_url": None,
            "metodo_pago": promo["metodo_pago"],
            "tarjeta_marca": promo.get("tarjeta_marca"),
            "comercio": promo["comercio"],
            "categoria": promo["categoria"],
            "porcentaje": promo["porcentaje"],
            "tope_reintegro": promo["tope_reintegro"],
            "dias_vigencia": dias,
            "fecha_inicio": promo["fecha_inicio"],
            "fecha_fin": promo["fecha_fin"],
            "link_detalle": promo["link_detalle"],
            "ultima_actualizacion": datetime.now().isoformat() + "Z"
        })
    
    descuentos = sorted(descuentos, key=lambda x: x['porcentaje'], reverse=True)
    
    for idx, d in enumerate(descuentos, 1):
        d['id'] = idx
    
    return {
        "descuentos": descuentos,
        "total": len(descuentos),
        "ultima_sincronizacion": datetime.now().isoformat() + "Z",
        "fuentes": ["BD Manual - Actualizado manualmente"]
    }

def guardar_data_json(data):
    """Guarda data.json"""
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    logger.info(f"✓ {data['total']} descuentos guardados")

if __name__ == "__main__":
    logger.info("=" * 70)
    logger.info("GENERADOR DATA.JSON - BD MANUAL")
    logger.info("=" * 70)
    
    promociones = cargar_promociones()
    data = generar_data_json(promociones)
    guardar_data_json(data)
    
    logger.info("✓ COMPLETADO")
    logger.info("=" * 70)
