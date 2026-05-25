import json
import logging
import requests
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def extraer_bbva():
    """Extrae promociones de BBVA via su API interna"""
    import re
    campaignIds = [2415, 2416, 2417, 2474, 2492, 2493, 2497, 2502, 2518, 2520, 2521]
    bbvaPromos = []
    
    for cid in campaignIds:
        try:
            # Página 1
            r = requests.get(f'https://go.bbva.com.ar/willgo/fgo/API/v3/campaign/{cid}')
            if r.status_code != 200:
                continue
            
            data = r.json()
            bbvaPromos.extend(data.get('data', []))
            
            # Obtener páginas adicionales
            message = data.get('message', '')
            if 'paginas:' in message:
                pages = int(message.split('paginas: ')[1].split()[0])
                for p in range(2, pages + 1):
                    r = requests.get(f'https://go.bbva.com.ar/willgo/fgo/API/v3/campaign/{cid}?page={p}')
                    if r.status_code == 200:
                        page_data = r.json()
                        if page_data.get('data'):
                            bbvaPromos.extend(page_data['data'])
        except Exception as e:
            logger.warning(f"Error extrayendo BBVA campaña {cid}: {e}")
    
    # Formatear
    bbvaFormatted = []
    for p in bbvaPromos:
        try:
            # Manejar diasPromo de forma robusta
            diasPromo = p.get('diasPromo')
            if diasPromo is None or diasPromo == '':
                diasStr = '1,1,1,1,1,1,1'
            else:
                diasStr = str(diasPromo)
            
            dias = []
            nombres = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            try:
                for i, v in enumerate(diasStr.split(',')):
                    if v.strip() == '1' and i < len(nombres):
                        dias.append(nombres[i])
            except:
                pass
            
            if not dias:
                dias = ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo']
            
            porcentaje = 0
            comercio = p.get('cabecera', '')
            
            # Extraer porcentaje
            match = re.search(r'(\d+)%', comercio)
            if match:
                porcentaje = int(match.group(1))
            
            # Limpiar comercio
            comercio = re.sub(r'\d+%.*', '', comercio)
            comercio = re.sub(r'\d+ cuotas.*', '', comercio).strip()
            if not comercio:
                comercio = p.get('cabecera', 'Promo BBVA')
            
            bbvaFormatted.append({
                'banco': 'BBVA',
                'comercio': comercio,
                'porcentaje': porcentaje,
                'tope_reintegro': int(p.get('montoTope', 0)) if p.get('montoTope') else None,
                'dias_vigencia': dias,
                'metodo_pago': p.get('grupoTarjeta', 'Tarjeta de Crédito'),
                'fecha_inicio': p.get('fechaDesde', ''),
                'fecha_fin': p.get('fechaHasta', ''),
                'link_detalle': f"https://www.bbva.com.ar/beneficios/beneficio?id={p.get('id')}",
                'id_original': p.get('id')
            })
        except Exception as e:
            logger.warning(f"Error procesando promo BBVA: {e}")
            continue
    
    logger.info(f"✓ Extraídas {len(bbvaFormatted)} promociones de BBVA")
    return bbvaFormatted

def extraer_santander():
    """Extrae promociones de Santander via su BFF API"""
    try:
        r = requests.get('https://www.santander.com.ar/bff-benefits/brands?limit=999')
        if r.status_code != 200:
            logger.warning(f"Error conectando a Santander: {r.status_code}")
            return []
        
        data = r.json()
        beneficios = data.get('items', [])
        
        santanderFormatted = []
        hoy = datetime.now().date()
        fin = hoy + timedelta(days=180)
        
        for b in beneficios:
            santanderFormatted.append({
                'banco': 'SANTANDER',
                'comercio': b.get('name', ''),
                'porcentaje': 0,  # Santander no lo proporciona
                'tope_reintegro': None,
                'dias_vigencia': ['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'],
                'metodo_pago': 'Tarjeta de Crédito',
                'fecha_inicio': str(hoy),
                'fecha_fin': str(fin),
                'link_detalle': f"https://www.santander.com.ar/personas/beneficios?brand={b.get('code', '')}",
                'id_original': b.get('id')
            })
        
        logger.info(f"✓ Extraídas {len(santanderFormatted)} promociones de SANTANDER")
        return santanderFormatted
    
    except Exception as e:
        logger.error(f"Error extrayendo Santander: {e}")
        return []

def combinar_y_guardar(bbva, santander):
    """Combina los datos y guarda en data.json"""
    combinado = {
        'descuentos': sorted(bbva + santander, key=lambda x: x['porcentaje'], reverse=True),
        'total': len(bbva) + len(santander),
        'por_banco': {
            'BBVA': len(bbva),
            'SANTANDER': len(santander)
        },
        'ultima_sincronizacion': datetime.now().isoformat() + 'Z',
        'fuentes': ['BBVA API Interna', 'Santander BFF API']
    }
    
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(combinado, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Guardados {combinado['total']} descuentos en data.json")
    return combinado

if __name__ == '__main__':
    logger.info("🚀 Iniciando extracción de promociones...")
    
    bbva = extraer_bbva()
    santander = extraer_santander()
    
    resultado = combinar_y_guardar(bbva, santander)
    
    logger.info(f"""
    ═══════════════════════════════════════
    ✓ EXTRACCIÓN COMPLETADA
    ═══════════════════════════════════════
    Total: {resultado['total']} promociones
    - BBVA: {resultado['por_banco']['BBVA']}
    - SANTANDER: {resultado['por_banco']['SANTANDER']}
    
    Archivo: data.json
    ═══════════════════════════════════════
    """)
