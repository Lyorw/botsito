from flask import Flask, request, jsonify
import http.client
import json
from preguntas import obtener_mensaje_bienvenida, manejar_respuesta_interactiva, validar_nombre_apellido

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAANytZCyISKIBO8KFhSQKYTSMEZCpWe5PxEfhl9ecEp2elewqm5KLJ23Fmk0ZA4JZAANavrAvPWknpGhf5EiwevBl9kTxIoPXLtZC6lwcNX4YU6I0l93T9uelC3nikXZA0ITZB6LXtlCIVYBDu3jO408Q3OaP110f5VXn5rndF8n1qeYZCZBDSaTl0pEx8ZBUZCRXivDVOZAqZCDA4SOERALxyq8Pfidkqw8ZD"

usuarios = {}

@app.route('/')
def index():
    return "Descargando virus."

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        return verificar_token(request)
    elif request.method == 'POST':
        return recibir_mensajes(request)

def verificar_token(req):
    token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    if challenge and token == TOKEN_ANDERCODE:
        return challenge
    else:
        return jsonify({'error': 'Token Inválido'}), 401

def recibir_mensajes(req):
    try:
        data = request.get_json()
        print("Data received:", data)

        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            numero = messages.get("from", "")
            text = messages.get("text", {}).get("body", "")
            
            if numero not in usuarios:
                usuarios[numero] = {"estado": None, "intentos": 0}

            estado_actual = usuarios[numero]["estado"]
            intentos = usuarios[numero]["intentos"]

            if estado_actual is None:  # Primera interacción
                if messages.get('type') == 'interactive':
                    reply_id = messages.get('interactive', {}).get('button_reply', {}).get('id', "")
                    respuesta, nuevo_estado, _ = manejar_respuesta_interactiva(reply_id, intentos)
                    usuarios[numero]["estado"] = nuevo_estado
                else:
                    respuesta = obtener_mensaje_bienvenida()
                    respuesta["to"] = numero
                    enviar_mensajes_whatsapp(respuesta, numero)
                    return jsonify({'message': 'EVENT_RECEIVED'})
            
            else:  # Validación de nombre o apellido
                respuesta, exito, intentos = validar_nombre_apellido(text, estado_actual, intentos)
                if exito:
                    usuarios[numero]["estado"] = None
                    usuarios[numero]["intentos"] = 0
                else:
                    usuarios[numero]["intentos"] = intentos

            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": respuesta
                }
            }
            enviar_mensajes_whatsapp(data, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'message': 'EVENT_RECEIVED', 'error': str(e)})

def enviar_mensajes_whatsapp(data, number):
    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {ACCESS_TOKEN}"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", f"/v20.0/{PAGE_ID}/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason, response.read().decode())
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
