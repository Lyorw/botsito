from flask import Flask, request, jsonify
import http.client
import json
import re
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta, verificar_usuario_registrado

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBO0ZCx8adHB7JxGG28D3IUdCTQstqr5kI1ZCSziTp4ALieZAP62NFoyinbZAGovIfZCj52UZAxVZCQ9jrGmI1V7zlZAs4db4rK48H5w1LIxFF6VASNCvMbfG6MXUJ5po1d15oOj1TpvKSQF78nITM45DaNNhjvHhu9K8v53wMLuplOkVcG3hJ2N56wpImh6SxE4QeDfOxl0Pi2S3tafYZD"

mensajes_procesados = set()
intentos_por_usuario = {}
esperando_respuesta = {}

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
        print("Data received:", data)

        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            numero = messages.get("from", "")
            mensaje_id = messages.get("id", "")
            texto_usuario = messages.get("text", {}).get("body", "").strip()

            if mensaje_id in mensajes_procesados:
                return jsonify({'status': 'Mensaje ya procesado'}), 200
            mensajes_procesados.add(mensaje_id)

            # Verificar si el usuario ya está registrado
            if verificar_usuario_registrado(numero):
                enviar_mensaje_texto(numero, "Usuario ya está registrado")
                return jsonify({'status': 'Usuario registrado'}), 200

            # Si no está registrado, manejar el flujo inicial
            if numero not in esperando_respuesta or not esperando_respuesta[numero]:
                enviar_mensaje_inicial(numero)
                esperando_respuesta[numero] = True
                intentos_por_usuario[numero] = 0  # Reiniciar intentos al comenzar desde el inicio
                return jsonify({'status': 'Mensaje inicial enviado'}), 200

            # Continuar solo si se ha seleccionado un botón
            if messages.get("type") == "interactive":
                interactive_obj = messages.get("interactive", {})
                button_reply = interactive_obj.get("button_reply", {})
                seleccion = button_reply.get("id", "")
                
                if seleccion == "button_yes":
                    mensaje_si = obtener_mensaje_por_id(2)
                    enviar_mensaje_texto(numero, mensaje_si)
                    intentos_por_usuario[numero] = 0  # Reiniciar intentos al pasar a la pregunta de correo
                    esperando_respuesta[numero] = False
                elif seleccion == "button_no":
                    enviar_mensaje_texto(numero, "Okey, nos vemos pronto")
                    esperando_respuesta[numero] = False
                
                return jsonify({'status': 'Respuesta a botón procesada'}), 200

            # Si llega un mensaje de texto cuando se espera un botón, ignorarlo
            if esperando_respuesta.get(numero, False):
                return jsonify({'status': 'Esperando respuesta a botón'}), 200

            # Lógica de validación de correo
            if not validar_correo(texto_usuario):
                intentos = intentos_por_usuario.get(numero, 0) + 1
                if intentos >= 2:
                    enviar_mensaje_texto(numero, "Correo inválido, nos vemos pronto.")
                    intentos_por_usuario[numero] = 0  # Reiniciar los intentos
                    enviar_mensaje_inicial(numero)
                    esperando_respuesta[numero] = True  # Esperar selección de botones nuevamente
                else:
                    enviar_mensaje_texto(numero, f"Correo inválido, por favor vuelva a ingresar. Intento {intentos}/2")
                    intentos_por_usuario[numero] = intentos
            else:
                enviar_mensaje_texto(numero, "Correo válido, continuamos con el proceso.")
                intentos_por_usuario.pop(numero, None)  # Borrar intentos después de éxito

            return jsonify({'status': 'Respuesta procesada'}), 200
        else:
            return jsonify({'error': 'No hay mensajes para procesar'}), 400
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

def enviar_mensaje_texto(numero, mensaje_texto):
    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje_texto
        }
    }
    enviar_mensaje(responder_mensaje)

def validar_correo(correo):
    patron = r'^[A-Za-z]{5,}@(globalhitss\.com|claro\.com\.pe)$'
    return re.match(patron, correo) is not None

def enviar_mensaje_inicial(numero):
    mensaje_db = obtener_mensaje_por_id(1)
    alternativas = obtener_alternativas_por_id_pregunta(1)

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
