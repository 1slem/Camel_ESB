from flask import Flask, request, jsonify, send_file
import json
import os
from datetime import datetime
from flask_cors import CORS  # Pour permettre les requêtes cross-origin

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes
app.debug = True
DATA_FILE = os.path.join(os.path.dirname(__file__), 'orders.json')

# Create empty orders.json if it doesn't exist
if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump([], f)

@app.route('/')
def home():
    return send_file('index.html')

@app.route('/orders')
def get_orders():
    try:
        app.logger.info('Attempting to read orders from %s', DATA_FILE)
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                app.logger.info('Successfully read %d orders', len(data))
                return jsonify(data)
        else:
            app.logger.warning('orders.json does not exist, creating empty file')
            with open(DATA_FILE, 'w', encoding='utf-8') as f:
                json.dump([], f)
            return jsonify([])
    except Exception as e:
        app.logger.error('Error reading orders: %s', str(e))
        return jsonify({'error': str(e)}), 500

@app.route('/ingest', methods=['POST'])
@app.route('/ingest/', methods=['POST'])
def ingest():
    app.logger.info('Received request: %s', request.get_data(as_text=True))
    # accept JSON or XML; we expect JSON from ESB
    content_type = request.headers.get('Content-Type','')
    if 'application/json' in content_type or request.is_json:
        order = request.get_json()
    else:
        # try to parse raw body as text
        order = {'raw': request.get_data(as_text=True)}

    # Ajouter la date de passage de commande si elle n'existe pas
    if 'orderDate' not in order:
        order['orderDate'] = datetime.now().isoformat()

    # persist
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
            except Exception:
                data = []
    else:
        data = []

    data.append(order)
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

    return jsonify({'status':'ok','stored': True}), 201

if __name__ == '__main__':
    app.run(port=5000)
