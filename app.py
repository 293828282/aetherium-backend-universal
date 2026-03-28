import os
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
import yfinance as yf

app = Flask(__name__)
# Abrimos la puerta para que tu compañero de frontend pueda entrar sin problemas
CORS(app, resources={r"/*": {"origins": "*"}})

# --- EL TRAJE DE CAMUFLAJE (DISFRAZ DE GOOGLE CHROME) ---
session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept": "*/*",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
})

@app.route('/')
def home():
    return jsonify({"status": "Motor Universal Activo", "tecnologia": "Python + yfinance"})

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

    # Pequeña ayuda: si alguien escribe solo CLP, lo arreglamos a CLP=X
    if ticker == "CLP":
        ticker = "CLP=X"

    try:
        # Aquí usamos la sesión camuflada para engañar al escudo
        activo = yf.Ticker(ticker, session=session)
        hist = activo.history(period=periodo)

        if hist.empty:
            return jsonify({"error": f"No se encontraron datos para {ticker}. Verifica el símbolo."}), 404

        resultados = []
        for date, row in hist.iterrows():
            resultados.append({
                "fecha": date.strftime('%Y-%m-%d'),
                "precio_cierre": round(row['Close'], 4)
            })

        return jsonify({
            "status": "success",
            "ticker": ticker,
            "total_registros": len(resultados),
            "datos": resultados
        })

    except Exception as e:
        return jsonify({"error": "Error interno del motor", "detalle": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
