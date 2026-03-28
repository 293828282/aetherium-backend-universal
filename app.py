import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

# Inicializar la aplicación y abrir todos los accesos (CORS)
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

@app.route('/')
def home():
    return jsonify({"status": "Motor Universal Activo", "tecnologia": "Python + yfinance"})

@app.route('/api/datos', methods=['GET', 'POST'])
def obtener_datos():
    # Acepta datos tanto por URL (GET) como por paquete JSON (POST) para facilitar la vida al frontend
    if request.method == 'POST':
        data = request.get_json() or {}
        ticker = data.get('ticker', 'AAPL')
        periodo = data.get('periodo', '1y') # Opciones: 1mo, 3mo, 6mo, 1y, 2y, 5y, max
    else:
        ticker = request.args.get('ticker', 'AAPL')
        periodo = request.args.get('periodo', '1y')

    ticker = ticker.upper().strip()

    try:
        # yfinance hace la magia de evadir los bloqueos aquí
        activo = yf.Ticker(ticker)
        hist = activo.history(period=periodo)

        if hist.empty:
            return jsonify({"error": f"No se encontraron datos para {ticker}. Verifica el símbolo."}), 404

        # Limpieza y formateo de datos para el frontend
        resultados = []
        for date, row in hist.iterrows():
            resultados.append({
                "fecha": date.strftime('%Y-%m-%d'),
                "precio_cierre": round(row['Close'], 4) # 4 decimales ideal para divisas
            })

        return jsonify({
            "status": "success",
            "ticker": ticker,
            "total_registros": len(resultados),
            "datos": resultados
        })

    except Exception as e:
        return jsonify({"error": "Error interno del motor", "detalle": str(e)}), 500

# Configuración para el servidor de producción
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
