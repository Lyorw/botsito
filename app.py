from flask import Flask, request, jsonify
import http.client
import json
from logica_mesajes import manejar_mensajes  # Importar función desde el otro archivo

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBO9EHKqeQkmLndJSNfvZCniqZBUZBji3SXYWz678zbuK3TdzZC8vLG8nF8ZBNlsoeBwtmCthPox62x8iKhHE19DtZAEIjcKtjVbNTsL7cMWKonZC0icywXEbCnvuy7lB1hreKbJB4JB9JbeaFXdO65gknLdZBLhrWkRP8Nb9c7duaMcIiOjry77IxP11l88NXQ6F4PcszNH03em8AbUYZD"

mensajes_procesados = set()
estado_usuario = {}

@app.route('/')
def index():
    return "Descargando virus..."

@app.route('/webhook', methods=['GET'])
def verificar_token():
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error': 'Token Inválido'}), 401

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    try:
        data = request.get_json()
        print("Data received:", data)

        response_message = manejar_mensajes(data, mensajes_procesados, estado_usuario, enviar_mensaje_texto)

        return jsonify({'status': response_message}), 200
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

def enviar_mensaje_texto(numero, mensaje_texto):
    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje_texto
        }
    }
    enviar_mensaje(responder_mensaje)

def enviar_mensaje(mensaje):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload = json.dumps(mensaje)
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    conn.request("POST", f"/v15.0/{PAGE_ID}/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print("Respuesta de Facebook API:", data.decode("utf-8"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
