from flask import Flask, request, jsonify
import http.client
import json
from preguntas import obtener_mensaje_bienvenida, manejar_respuesta_interactiva, validar_nombre_apellido

app = Flask(__name__)

# Configuración de variables
TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAANytZCyISKIBO5rde4yb75NwJctkw17D6l94biffuEUJtC5hZA7HjL7ZBeUn9rAIexepgRXIwDHhhPKZA22fPds5Wztt3WXdVKT3I4ZBjGZC2zeZCcWRU66BJB5zGhbJccmalG7miZB3RfMRQ8q7wBr74fZAGiUJZBiKSEZB7uJZCi3fJYq7i5MXPY7ZAZAA1L4yELyQB1ZC9jlTbU4hoWynGPb4TFbnxKmP0ZD"

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
        print("Data received:", data)  # Verifica los datos recibidos

        entry = data.get('entry', [{}])[0]
        changes = entry.get('changes', [{}])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            text = messages.get("text", {}).get("body", "")
            numero = messages.get("from", "")

            print(f"Received message from {numero}: {text}")  # Verifica el mensaje recibido

            if numero not in intentos_nombre:
                intentos_nombre[numero] = 0
                intentos_apellido[numero] = 0

            if intentos_nombre[numero] < 2:  # Pregunta de nombre
                respuesta, correcto = validar_nombre_apellido(text, intentos_nombre[numero], "nombre")
                if correcto:
                    if "nombre" in respuesta.lower():
                        intentos_nombre[numero] = 2  # Bloquear la pregunta de nombre
                        respuesta = "Gracias, ahora ¿cuáles son tus apellidos?"
                else:
                    respuesta = respuesta

            elif intentos_apellido[numero] < 2:  # Pregunta de apellido
                respuesta, correcto = validar_nombre_apellido(text, intentos_apellido[numero], "apellido")
                if correcto:
                    respuesta = "¡Perfecto! Gracias por completar el formulario."
                    intentos_apellido[numero] = 2  # Bloquear la pregunta de apellido
                else:
                    respuesta = respuesta

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
    print(f"Sending message to {number}: {data}")  # Agrega esto para depuración

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
