from flask import Flask, request, jsonify
import http.client
import json
import re
from conexionbd import obtener_mensaje_por_id, verificar_usuario_registrado

app = Flask(__name__)

TOKEN_ANDERCODE = "ANDERCODE"
PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBO3q0Qr3D26pKA9wTWztyng7ZA1miM0ZA1W2onKQvkFsuvImZCx12IrtQYMUD06PcloyT5PZA7xmqPMZBAqPYWtUlBOKjZCOqS6ZA9dIIOHZAN2nn0gS2mryDS39zcs7FegXhgFjSjoWZCr91GC0WO6fOiLkgkPdah5njDGcEQUsZBHByH8DRTPSiB0gVZAIkiUD7aMymEDZA6sQQ8r0L8LMZD"

mensajes_procesados = set()
estado_usuario = {}

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

def validar_nombre(nombre):
    return not any(char.isdigit() for char in nombre)

def validar_numero(numero):
    return numero.isdigit() and 5 <= len(numero) <= 20

def validar_codigo(codigo):
    if len(codigo) < 2:
        return False
    
    letra = codigo[0].upper()
    numeros = codigo[1:]
    
    if not letra.isalpha() or not numeros.isdigit():
        return False
    
    if letra == "E":
        return 5 <= len(codigo) <= 6
    elif letra == "C":
        return 5 <= len(codigo) <= 8
    elif letra == "D":
        return 10 <= len(codigo) <= 15
    else:
        return False

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

            if numero not in estado_usuario:
                estado_usuario[numero] = {
                    "intentos_codigo": 0,
                    "esperando_codigo": False,
                    "autenticacion_confirmada": False
                }
                enviar_mensaje_inicial(numero)
                return jsonify({'status': 'Mensaje inicial enviado'}), 200

            if verificar_usuario_registrado(numero):
                enviar_mensaje_texto(numero, "Usuario ya está registrado")
                return jsonify({'status': 'Usuario registrado'}), 200

            if messages.get("type") == "interactive":
                interactive_obj = messages.get("interactive", {})
                button_reply = interactive_obj.get("button_reply", {})
                seleccion = button_reply.get("id", "")
                
                if seleccion == "button_yes":
                    mensaje_si = obtener_mensaje_por_id(2)
                    enviar_mensaje_texto(numero, mensaje_si)
                    estado_usuario[numero]["esperando_codigo"] = True
                    estado_usuario[numero]["autenticacion_confirmada"] = True
                elif seleccion == "button_no":
                    enviar_mensaje_texto(numero, "Okey, nos vemos pronto")
                    estado_usuario.pop(numero, None)
                return jsonify({'status': 'Respuesta a botón procesada'}), 200

            if estado_usuario[numero].get("esperando_codigo", False):
                if validar_codigo(texto_usuario):
                    estado_usuario[numero]["esperando_codigo"] = False
                    enviar_mensaje_texto(numero, "Gracias, puede proceder.")
                else:
                    estado_usuario[numero]["intentos_codigo"] += 1
                    if estado_usuario[numero]["intentos_codigo"] == 1:
                        enviar_mensaje_texto(numero, "Código inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_codigo"] == 2:
                        enviar_mensaje_texto(numero, "Código inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de código procesado'}), 200
            
            return jsonify({'status': 'Respuesta procesada'}), 200
        else:
            return jsonify({'error': 'No hay mensajes para procesar'}), 400
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

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
