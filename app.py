from flask import Flask, request, jsonify
import http.client
import json
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"  # Reemplaza con tu ID de página
ACCESS_TOKEN = "EAAYAnB4BMXoBO0ZCx8adHB7JxGG28D3IUdCTQstqr5kI1ZCSziTp4ALieZAP62NFoyinbZAGovIfZCj52UZAxVZCQ9jrGmI1V7zlZAs4db4rK48H5w1LIxFF6VASNCvMbfG6MXUJ5po1d15oOj1TpvKSQF78nITM45DaNNhjvHhu9K8v53wMLuplOkVcG3hJ2N56wpImh6SxE4QeDfOxl0Pi2S3tafYZD"

# Un conjunto para almacenar los identificadores de mensajes ya procesados
mensajes_procesados = set()

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
        print("Data received:", data)  # Para depuración

        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            numero = messages.get("from", "")
            mensaje_id = messages.get("id", "")

            # Verificar si el mensaje ya ha sido procesado
            if mensaje_id in mensajes_procesados:
                return jsonify({'status': 'Mensaje ya procesado'}), 200
            mensajes_procesados.add(mensaje_id)

            # Obtener el mensaje inicial desde la base de datos
            mensaje_db = obtener_mensaje_por_id(1)  # ID 1 para el mensaje inicial
            alternativas = obtener_alternativas_por_id_pregunta(2)  # ID 2 para alternativas
            
            botones = [
                {
                    "type": "reply",
                    "reply": {
                        "id": "button_yes",
                        "title": alternativas[0] if len(alternativas) > 0 else "Sí"
                    }
                },
                {
                    "type": "reply",
                    "reply": {
                        "id": "button_no",
                        "title": alternativas[1] if len(alternativas) > 1 else "No"
                    }
                }
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
                        "buttons": botones
                    }
                }
            }
            enviar_mensaje(responder_mensaje)
            return jsonify({'status': 'Mensaje enviado'}), 200
        else:
            return jsonify({'error': 'No hay mensajes para procesar'}), 400
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

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
