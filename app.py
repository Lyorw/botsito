from flask import Flask, request, jsonify
import http.client
import json
from preguntas import obtener_mensaje_bienvenida, manejar_respuesta_interactiva, validar_nombre_apellido

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAANytZCyISKIBO8KFhSQKYTSMEZCpWe5PxEfhl9ecEp2elewqm5KLJ23Fmk0ZA4JZAANavrAvPWknpGhf5EiwevBl9kTxIoPXLtZC6lwcNX4YU6I0l93T9uelC3nikXZA0ITZB6LXtlCIVYBDu3jO408Q3OaP110f5VXn5rndF8n1qeYZCZBDSaTl0pEx8ZBUZCRXivDVOZAqZCDA4SOERALxyq8Pfidkqw8ZD"

intentos_nombre = {}
intentos_apellido = {}

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

        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            text = messages.get("text", {}).get("body", "")
            numero = messages.get("from", "")

            if numero not in intentos_nombre:
                intentos_nombre[numero] = 0
                intentos_apellido[numero] = 0

            if intentos_nombre[numero] < 2:  # Pregunta de nombre
                intentos_nombre[numero] += 1
                respuesta, correcto = validar_nombre_apellido(text, intentos_nombre[numero], "nombre")
                if correcto and "nombre" in respuesta.lower():
                    intentos_nombre[numero] = 2  # Bloquear la pregunta de nombre

            elif intentos_apellido[numero] < 2:  # Pregunta de apellido
                intentos_apellido[numero] += 1
                respuesta, correcto = validar_nombre_apellido(text, intentos_apellido[numero], "apellido")
                if correcto and "¡perfecto!" in respuesta.lower():
                    intentos_apellido[numero] = 2  # Bloquear la pregunta de apellido
                    respuesta = "Gracias por completar el formulario."  # Mensaje final

            else:  # Redirigir al inicio después de los intentos fallidos
                respuesta = obtener_mensaje_bienvenida()

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

        elif 'interactive' in messages:  # Manejo de interacciones
            reply_id = messages.get('interactive', {}).get('button_reply', {}).get('id', "")
            responder_mensaje = manejar_respuesta_interactiva(reply_id)

            data = {
                "messaging_product": "whatsapp",
                "recipient_type": "individual",
                "to": numero,
                "type": "text",
                "text": {
                    "preview_url": False,
                    "body": responder_mensaje
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
