import os
import requests
from datetime import datetime
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
# Accesos abiertos para cualquier frontend
CORS(app, resources={r"/*": {"origins": "*"}})

def extraccion_silenciosa(ticker, periodo):
    # Conexión directa a la API oculta de Yahoo, saltando los bloqueos de librerías
    url = f"https://query2.finance.yahoo.com/v8/finance/chart/{ticker}?range={periodo}&interval=1d"
    
    # Disfraz ligero
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
    }
    
    try:
        respuesta = requests.get(url, headers=headers, timeout=10)
        
        if respuesta.status_code != 200:
            return None
            
        data = respuesta.json()
        
        # Navegamos por el JSON interno de Yahoo para sacar justo lo que necesitamos
        resultado = data['chart']['result'][0]
        fechas_unix = resultado['timestamp']
        precios = resultado['indicators']['quote'][0]['close']
        
        historial = []
        # Emparejamos cada fecha con su precio
        for t, precio in zip(fechas_unix, precios):
            if precio is not None: # A veces Yahoo manda días vacíos (feriados)
                # Convertimos el código de tiempo de la máquina a fecha real (YYYY-MM-DD)
                fecha_real = datetime.utcfromtimestamp(t).strftime('%Y-%m-%d')
                historial.append({
                    "fecha": fecha_real,
                    "precio_cierre": round(precio, 4)
                })
                
        return historial
    except Exception as e:
        print(f"Error en extracción: {e}")
        return None

@app.route('/')
def home():
    return jsonify({"status": "Motor Universal Activo", "metodo": "Extracción Quirúrgica Directa"})

@app.route('/api/datos', methods=['GET', 'POST'])
def obtener_datos():
    if request.method == 'POST':
        data = request.get_json() or {}
        ticker = data.get('ticker', 'AAPL')
        periodo = data.get('periodo', '1y')
    else:
        ticker = request.args.get('ticker', 'AAPL')
        periodo = request.args.get('periodo', '1y')

    ticker = ticker.upper().strip()

    if ticker == "CLP":
        ticker = "CLP=X"

    # Llamamos a nuestra nueva función anti-escudos
    datos = extraccion_silenciosa(ticker, periodo)

    if not datos:
        return jsonify({"error": f"No se encontraron datos para {ticker}. El mercado puede estar cerrado o el símbolo no existe."}), 404

    return jsonify({
        "status": "success",
        "ticker": ticker,
        "total_registros": len(datos),
        "datos": datos
    })

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
