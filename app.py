from flask import Flask, request, jsonify
import http.client
import json

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"  # Reemplaza con tu ID de página
ACCESS_TOKEN = "EAANytZCyISKIBOyK0RaoUyGvB6G1TXiNOtjQn5d2a8J7mlzyUZB5pTdZBYrQUlhCkvIPCvdtCHID6i0k2qOOe4ZBXe6S8EeH5XNyRKUvImQuK4Muiu9IGqMTjkZCEEk5kdEbOx3EQ80Jd6nvhlb6RdN788PXnqSZCJjsFcpkZBHWBzHBFxcMR9ciyYffb0SaXchoaLCFxyg9ptTVng3H92S0wxbgBkZD"

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
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            if messages.get('type') == 'text':
                text = messages.get("text", {}).get("body", "")
                numero = messages.get("from", "")

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
                                    "😊 ¡Hola! Bienvenido/a a nuestro chatbot de autenticación. Estoy aquí para ayudarte a completar el proceso de manera rápida y segura. Antes de comenzar, ¿estás de acuerdo en llevar a cabo este proceso de autenticación? Por favor, responde con 'Sí' para continuar o 'No' si prefieres no seguir adelante."
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
            elif messages.get('type') == 'interactive':
                reply_id = messages.get('interactive', {}).get('button_reply', {}).get('id', "")
                numero = messages.get("from", "")

                if reply_id == "si_button":
                    responder_mensaje = "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)"
                elif reply_id == "no_button":
                    responder_mensaje = "Okey, nos vemos pronto."
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
