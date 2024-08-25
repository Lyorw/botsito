from flask import Flask, request, jsonify
import http.client
import json

app = Flask(__name__)

# Token de verificación para la configuración
TOKEN_ANDERCODE = "ANDERCODE"

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
        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            if "text" in messages:
                text = messages["text"]["body"]
                numero = messages["from"]

                # Responder con botones si el mensaje es el primero
                if "😊" not in text:
                    responder_mensaje = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": numero,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text": (
                                    "😊 ¡Hola! Bienvenido/a a nuestro chatbot de autenticación. "
                                    "Estoy aquí para ayudarte a completar el proceso de manera rápida y segura. "
                                    "Antes de comenzar, ¿estás de acuerdo en llevar a cabo este proceso de autenticación? "
                                    "Por favor, elige una opción a continuación."
                                )
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "si_button",
                                            "title": "Sí"
                                        }
                                    },
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "no_button",
                                            "title": "No"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                    enviar_mensajes_whatsapp(responder_mensaje, numero)
                elif "reply" in messages:
                    if messages["reply"]["id"] == "si_button":
                        responder_mensaje = "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)"
                        enviar_mensajes_whatsapp_texto(responder_mensaje, numero)
                    elif messages["reply"]["id"] == "no_button":
                        responder_mensaje = "Okey, nos vemos pronto."
                        enviar_mensajes_whatsapp_texto(responder_mensaje, numero)

        return jsonify({'message': 'EVENT_RECEIVED'})
    except Exception as e:
        return jsonify({'message': 'EVENT_RECEIVED', 'error': str(e)})

def enviar_mensajes_whatsapp(data, number):
    # Convertir el diccionario a formato JSON
    data = json.dumps(data)

    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer EAANytZCyISKIBO8KFhSQKYTSMEZCpWe5PxEfhl9ecEp2elewqm5KLJ23Fmk0ZA4JZAANavrAvPWknpGhf5EiwevBl9kTxIoPXLtZC6lwcNX4YU6I0l93T9uelC3nikXZA0ITZB6LXtlCIVYBDu3jO408Q3OaP110f5VXn5rndF8n1qeYZCZBDSaTl0pEx8ZBUZCRXivDVOZAqZCDA4SOERALxyq8Pfidkqw8ZD"
    }

    connection = http.client.HTTPSConnection("graph.facebook.com")

    try:
        connection.request("POST", "/v20.0/421866537676248/messages", data, headers)
        response = connection.getresponse()
        print(response.status, response.reason, response.read().decode())
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
    finally:
        connection.close()

def enviar_mensajes_whatsapp_texto(texto, number):
    data = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": number,
        "type": "text",
        "text": {
            "preview_url": False,
            "body": texto
        }
    }
    enviar_mensajes_whatsapp(data, number)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
