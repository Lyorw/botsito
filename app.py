from flask import Flask, request, jsonify
import http.client
import json

app = Flask(__name__)

ACCESS_TOKEN = "EAASSqJjOXnUBO6nquvezk6ZBO95Q7GIjKenBuT5tY4uaIjnDjD1hytikDlcZA0aDoYBPPrtBZCDCuQkcM4fBGPWIdK0ZAbXEYOZAd8ixatuoHbgQu0wtjiD08AZCj5JXlzJyQn7ad3N0LAhkTZAdIMpRnjIG5B8lkPmq00fgaf3iaPR9ZC6BLFwGHukG4Om3fc3rZB1Yv3vZCJuzz8atQ7sQarsIONjx8a1H4pPewZD"
PAGE_ID = "421866537676248"

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    numero = data.get('numero')
    mensaje_texto = data.get('mensaje_texto')
    
    if not numero or not mensaje_texto:
        return jsonify({'error': 'Falta el número o el mensaje'}), 400

    try:
        enviar_mensaje_texto(numero, mensaje_texto)
        return jsonify({'status': 'Mensaje enviado'}), 200
    except Exception as e:
        print(f"Error al enviar mensaje: {str(e)}")  # Añadir impresión para depuración
        return jsonify({'error': str(e)}), 500

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
    app.run(host='0.0.0.0', port=80)
