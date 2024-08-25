from flask import Flask, request, jsonify
import http.client
import json

app = Flask(__name__)

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
        print("Data received:", data)  # Verificar la estructura del mensaje recibido

        entry = data['entry'][0]
        changes = entry['changes'][0]
        value = changes['value']
        objeto_mensaje = value['messages']

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            if "text" in messages:
                text = messages["text"]["body"]
                numero = messages["from"]

                if "boton" in text:
                    data = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": numero,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text": "¿Confirmas tu registro?"
                            },
                            "footer": {
                                "text": "Selecciona una de las opciones"
                            },
                            "action": {
                                "buttons": [
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "btnsi",
                                            "title": "Si"
                                        }
                                    },
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "btnno",
                                            "title": "No"
                                        }
                                    },
                                    {
                                        "type": "reply",
                                        "reply": {
                                            "id": "btntalvez",
                                            "title": "Tal Vez"
                                        }
                                    }
                                ]
                            }
                        }
                    }
                    enviar_mensajes_whatsapp(data, numero)
                elif "reply" in messages:
                    reply_id = messages["reply"]["id"]
                    if reply_id == "btnsi":
                        responder_mensaje = "Muchas Gracias por Aceptar."
                    elif reply_id == "btnno":
                        responder_mensaje = "Es una Lastima."
                    elif reply_id == "btntalvez":
                        responder_mensaje = "Estaré a la espera."
                    else:
                        responder_mensaje = "Opción no reconocida."

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
        print(f"Error: {e}")  # Imprimir el error para depuración
        return jsonify({'message': 'EVENT_RECEIVED', 'error': str(e)})

def enviar_mensajes_whatsapp(data, number):
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
