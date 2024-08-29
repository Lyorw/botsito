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

            # Ignorar mensajes anteriores y solo procesar nuevos
            if mensaje_id in mensajes_procesados:
                return jsonify({'status': 'Mensaje ya procesado'}), 200
            mensajes_procesados.add(mensaje_id)

            # Inicialización del estado del usuario si no existe
            if numero not in estado_usuario:
                estado_usuario[numero] = {"intentos": 0, "esperando_correo": False, "autenticacion_confirmada": False, "recordatorio_enviado": False}
                enviar_mensaje_inicial(numero)  # Enviar mensaje de bienvenida con botones
                return jsonify({'status': 'Mensaje inicial enviado'}), 200

            # Verificar si el usuario ya está registrado
            if verificar_usuario_registrado(numero):
                enviar_mensaje_texto(numero, "Usuario ya está registrado")
                return jsonify({'status': 'Usuario registrado'}), 200

            # Continuar solo si se ha seleccionado un botón
            if messages.get("type") == "interactive":
                interactive_obj = messages.get("interactive", {})
                button_reply = interactive_obj.get("button_reply", {})
                seleccion = button_reply.get("id", "")
                
                if seleccion == "button_yes":
                    # Confirmar autenticación
                    mensaje_si = obtener_mensaje_por_id(2)
                    enviar_mensaje_texto(numero, mensaje_si)
                    estado_usuario[numero]["esperando_correo"] = True
                    estado_usuario[numero]["autenticacion_confirmada"] = True
                    estado_usuario[numero]["recordatorio_enviado"] = False  # Reiniciar recordatorio
                elif seleccion == "button_no":
                    enviar_mensaje_texto(numero, "Okey, nos vemos pronto")
                    estado_usuario.pop(numero, None)  # Eliminar estado para reiniciar
                return jsonify({'status': 'Respuesta a botón procesada'}), 200

            # Si no se ha seleccionado "Sí" o "No", enviar mensaje inicial
            if not estado_usuario[numero]["autenticacion_confirmada"]:
                if not estado_usuario[numero]["recordatorio_enviado"]:
                    enviar_mensaje_texto(numero, "Por favor, escoja uno de los botones para continuar: 'Sí' o 'No'.")
                    estado_usuario[numero]["recordatorio_enviado"] = True
                return jsonify({'status': 'Esperando selección de botón'}), 200

            # Ajustes dentro del método 'recibir_mensajes'
            if estado_usuario[numero]["esperando_correo"]:
                if not validar_correo(texto_usuario):
                    estado_usuario[numero]["intentos"] += 1
                    if estado_usuario[numero]["intentos"] == 1:
                        enviar_mensaje_texto(numero, "Correo inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos"] == 2:
                        enviar_mensaje_texto(numero, "Correo inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)  # Reiniciar después del segundo intento fallido
                else:
                    # Correo es válido, pasar al ID=3
                    mensaje_nombre = obtener_mensaje_por_id(3)
                    enviar_mensaje_texto(numero, mensaje_nombre)
                    estado_usuario[numero] = {"intentos": 0, "esperando_nombre": True}  # Ajuste aquí
                return jsonify({'status': 'Intento de correo procesado'}), 200

            # Nueva lógica para manejar el ID=3
            if estado_usuario[numero].get("esperando_nombre", False):
                if validar_nombre(texto_usuario):  # Implementa esta función para validar que no haya números
                    enviar_mensaje_texto(numero, "Nombre válido, puede continuar.")
                    estado_usuario.pop(numero, None)  # Limpiar estado en caso de éxito
                    # Aquí podrías pasar al siguiente ID o proceso
                else:
                    estado_usuario[numero]["intentos"] += 1
                    if estado_usuario[numero]["intentos"] == 1:
                        enviar_mensaje_texto(numero, "Nombre inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos"] == 2:
                        enviar_mensaje_texto(numero, "Nombre inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)  # Reiniciar después del segundo intento fallido
                return jsonify({'status': 'Intento de nombre procesado'}), 200

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
