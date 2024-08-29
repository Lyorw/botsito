from flask import Flask, request, jsonify
import http.client
import json
import pymssql
import requests

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"  # Reemplaza con tu ID de página
ACCESS_TOKEN = "EAAYAnB4BMXoBO0ZCx8adHB7JxGG28D3IUdCTQstqr5kI1VZCSziTp4ALieZAP62NFoyinbZAGovIfZCj52UZAxVZCQ9jrGmI1V7zlZAs4db4rK48H5w1LIxFF6VASNCvMbfG6MXUJ5po1d15oOj1TpvKSQF78nITM45DaNNhjvHhu9K8v53wMLuplOkVcG3hJ2N56wpImh6SxE4QeDfOxl0Pi2S3tafYZD"

def obtener_ip_publica():
    try:
        response = requests.get('https://api.ipify.org')
        ip_publica = response.text
        return ip_publica
    except requests.RequestException as e:
        print(f"Error al obtener la IP pública: {e}")
        return None

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
        print("Data received:", data)

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
                    mensaje_bd = obtener_mensaje_bd()
                    print(f"Mensaje obtenido de la base de datos: {mensaje_bd}")

                    responder_mensaje = {
                        "messaging_product": "whatsapp",
                        "recipient_type": "individual",
                        "to": numero,
                        "type": "interactive",
                        "interactive": {
                            "type": "button",
                            "body": {
                                "text": mensaje_bd
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
    # Obtener y mostrar la IP pública al iniciar la aplicación
    ip_publica = obtener_ip_publica()
    if ip_publica:
        print(f"La IP pública de la instancia es: {ip_publica}")

    app.run(host='0.0.0.0', port=80, debug=True)
