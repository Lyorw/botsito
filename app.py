from flask import Flask, request, jsonify
import http.client
import json
import pymssql

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"  # Reemplaza con tu ID de página
ACCESS_TOKEN = "EAAYAnB4BMXoBO0ZCx8adHB7JxGG28D3IUdCTQstqr5kI1ZCSziTp4ALieZAP62NFoyinbZAGovIfZCj52UZAxVZCQ9jrGmI1V7zlZAs4db4rK48H5w1LIxFF6VASNCvMbfG6MXUJ5po1d15oOj1TpvKSQF78nITM45DaNNhjvHhu9K8v53wMLuplOkVcG3hJ2N56wpImh6SxE4QeDfOxl0Pi2S3tafYZD"

# Función para obtener el mensaje de la base de datos
def obtener_mensaje_bd():
    server = 'chatwsp.database.windows.net'
    database = 'chatbot'
    username = 'wspbot'
    password = 'B@t264as'

    try:
        # Establecer conexión con la base de datos
        conn = pymssql.connect(server=server, user=username, password=password, database=database)
        cursor = conn.cursor()

        # Ejecutar la consulta
        cursor.execute("SELECT formulario FROM Preguntas WHERE ID = 1")
        row = cursor.fetchone()

        if row:
            return row[0]
        else:
            return "No se encontró el mensaje en la base de datos."

    except pymssql.Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return "Error al obtener el mensaje de la base de datos."
    
    finally:
        if conn:
            conn.close()

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
                    # Obtener mensaje desde la base de datos
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
