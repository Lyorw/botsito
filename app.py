from flask import Flask, request, jsonify
import http.client
import json
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"  # Reemplaza con tu ID de página
ACCESS_TOKEN = "EAAYAnB4BMXoBO0ZCx8adHB7JxGG28D3IUdCTQstqr5kI1ZCSziTp4ALieZAP62NFoyinbZAGovIfZCj52UZAxVZCQ9jrGmI1V7zlZAs4db4rK48H5w1LIxFF6VASNCvMbfG6MXUJ5po1d15oOj1TpvKSQF78nITM45DaNNhjvHhu9K8v53wMLuplOkVcG3hJ2N56wpImh6SxE4QeDfOxl0Pi2S3tafYZD"

@app.route('/')
def index():
    return "Descargando virus..."

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

        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            if messages.get('type') == 'text':
                text = messages.get("text", {}).get("body", "")
                numero = messages.get("from", "")

                if "😊" not in text:
                    mensaje_db = obtener_mensaje_por_id(1)
                    if not mensaje_db:
                        mensaje_db = "No se pudo obtener el mensaje de la base de datos."

                    alternativas = obtener_alternativas_por_id_pregunta(1)
                    buttons = [
                        {
                            "type": "reply",
                            "reply": {
                                "id": f"button_{i}",
                                "title": alternativa
                            }
                        }
                        for i, alternativa in enumerate(alternativas)
                    ]

                    responder_mensaje = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": numero,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text": mensaje_db
                            },
                            "action": {
                                "buttons": buttons
                            }
                        }
                    }
                    print("Mensaje a enviar:", json.dumps(responder_mensaje, indent=2))  # Verificar el contenido del mensaje
                    enviar_mensajes_whatsapp(responder_mensaje, numero)
            elif messages.get('type') == 'interactive':
                reply_id = messages.get('interactive', {}).get('button_reply', {}).get('id', "")
                numero = messages.get("from", "")

                if reply_id.startswith("button_"):
                    responder_mensaje = "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)"
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
                print("Mensaje a enviar:", json.dumps(data, indent=2))  # Verificar el contenido del mensaje
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
        response_data = response.read().decode()
        print(response.status, response.reason, response_data)
    except Exception as e:
        print(f"Error al enviar el mensaje: {e}")
    finally:
        connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80, debug=True)
