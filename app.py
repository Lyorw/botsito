from flask import Flask, request, jsonify
import http.client
import json
import re
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta, verificar_usuario_registrado

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

            # Ignorar mensajes anteriores y solo procesar nuevos
            if mensaje_id in mensajes_procesados:
                return jsonify({'status': 'Mensaje ya procesado'}), 200
            mensajes_procesados.add(mensaje_id)

            # Inicialización del estado del usuario si no existe
            if numero not in estado_usuario:
                estado_usuario[numero] = {
                    "intentos_correo": 0,
                    "intentos_nombre": 0,
                    "intentos_apellido": 0,
                    "intentos_numero": 0,
                    "intentos_codigo": 0,
                    "esperando_correo": False,
                    "esperando_nombre": False,
                    "esperando_apellido": False,
                    "esperando_numero": False,
                    "esperando_codigo": False,
                    "autenticacion_confirmada": False,
                    "recordatorio_enviado": False,
                    "esperando_pregunta_7": False,
                    "pagina_actual": 0  # Para manejar la paginación
                }
                enviar_mensaje_inicial(numero)
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
                    mensaje_si = obtener_mensaje_por_id(2)
                    enviar_mensaje_texto(numero, mensaje_si)
                    estado_usuario[numero]["esperando_correo"] = True
                    estado_usuario[numero]["autenticacion_confirmada"] = True
                    estado_usuario[numero]["recordatorio_enviado"] = False
                elif seleccion == "button_no":
                    enviar_mensaje_texto(numero, "Okey, nos vemos pronto")
                    estado_usuario.pop(numero, None)
                elif seleccion == "siguiente":
                    estado_usuario[numero]["pagina_actual"] += 1
                    enviar_mensaje_opciones(numero, estado_usuario[numero]["pagina_actual"])
                elif seleccion == "anterior":
                    estado_usuario[numero]["pagina_actual"] -= 1
                    enviar_mensaje_opciones(numero, estado_usuario[numero]["pagina_actual"])
                else:
                    # Aquí procesarías la opción seleccionada en lugar de navegación
                    enviar_mensaje_texto(numero, "Gracias por seleccionar una opción.")
                return jsonify({'status': 'Respuesta a botón procesada'}), 200

            # Si no se ha seleccionado "Sí" o "No", enviar mensaje inicial
            if not estado_usuario[numero].get("autenticacion_confirmada", False):
                if not estado_usuario[numero].get("recordatorio_enviado", False):
                    enviar_mensaje_texto(numero, "Por favor, escoja uno de los botones para continuar: 'Sí' o 'No'.")
                    estado_usuario[numero]["recordatorio_enviado"] = True
                return jsonify({'status': 'Esperando selección de botón'}), 200

            # Ajustes para manejar correo electrónico
            if estado_usuario[numero].get("esperando_correo", False):
                if not validar_correo(texto_usuario):
                    estado_usuario[numero]["intentos_correo"] += 1
                    if estado_usuario[numero]["intentos_correo"] == 1:
                        enviar_mensaje_texto(numero, "Correo inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_correo"] == 2:
                        enviar_mensaje_texto(numero, "Correo inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                else:
                    mensaje_nombre = obtener_mensaje_por_id(3)
                    enviar_mensaje_texto(numero, mensaje_nombre)
                    estado_usuario[numero]["intentos_nombre"] = 0
                    estado_usuario[numero]["esperando_nombre"] = True
                    estado_usuario[numero]["esperando_correo"] = False
                return jsonify({'status': 'Intento de correo procesado'}), 200

            # Manejo para nombres (ID=3)
            if estado_usuario[numero].get("esperando_nombre", False):
                if validar_nombre(texto_usuario):
                    estado_usuario[numero]["esperando_nombre"] = False
                    estado_usuario[numero]["esperando_apellido"] = True
                    mensaje_apellido = obtener_mensaje_por_id(4)
                    enviar_mensaje_texto(numero, mensaje_apellido)
                else:
                    estado_usuario[numero]["intentos_nombre"] += 1
                    if estado_usuario[numero]["intentos_nombre"] == 1:
                        enviar_mensaje_texto(numero, "Nombre inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_nombre"] == 2:
                        enviar_mensaje_texto(numero, "Nombre inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de nombre procesado'}), 200

            # Manejo para apellidos (ID=4)
            if estado_usuario[numero].get("esperando_apellido", False):
                if validar_nombre(texto_usuario):
                    estado_usuario[numero]["esperando_apellido"] = False
                    estado_usuario[numero]["esperando_numero"] = True
                    mensaje_numero = obtener_mensaje_por_id(5)
                    enviar_mensaje_texto(numero, mensaje_numero)
                else:
                    estado_usuario[numero]["intentos_apellido"] += 1
                    if estado_usuario[numero]["intentos_apellido"] == 1:
                        enviar_mensaje_texto(numero, "Apellido inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_apellido"] == 2:
                        enviar_mensaje_texto(numero, "Apellido inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de apellido procesado'}), 200

            # Manejo para número (ID=5)
            if estado_usuario[numero].get("esperando_numero", False):
                if validar_numero(texto_usuario):
                    estado_usuario[numero]["esperando_numero"] = False
                    estado_usuario[numero]["esperando_codigo"] = True
                    mensaje_codigo = obtener_mensaje_por_id(6)
                    enviar_mensaje_texto(numero, mensaje_codigo)
                else:
                    estado_usuario[numero]["intentos_numero"] += 1
                    if estado_usuario[numero]["intentos_numero"] == 1:
                        enviar_mensaje_texto(numero, "Número inválido, por favor vuelva a ingresar. Intento 1/2")
                    elif estado_usuario[numero]["intentos_numero"] == 2:
                        enviar_mensaje_texto(numero, "Número inválido, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
                return jsonify({'status': 'Intento de número procesado'}), 200

            # Manejo para código (ID=6)
            if estado_usuario[numero].get("esperando_codigo", False):
                if validar_codigo(texto_usuario):
                    estado_usuario[numero]["esperando_codigo"] = False
                    estado_usuario[numero]["esperando_pregunta_7"] = True
                    estado_usuario[numero]["pagina_actual"] = 0  # Inicializar a la primera página
                    enviar_mensaje_opciones(numero, estado_usuario[numero]["pagina_actual"])
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

def enviar_mensaje_opciones(numero, pagina):
    mensaje_pregunta_7 = obtener_mensaje_por_id(7)
    alternativas_pregunta_7 = obtener_alternativas_por_id_pregunta(7)

    # Número máximo de botones por página
    max_botones_por_pagina = 3

    # Calcular las opciones para mostrar en la página actual
    inicio = pagina * max_botones_por_pagina
    fin = inicio + max_botones_por_pagina
    opciones_pagina_actual = alternativas_pregunta_7[inicio:fin]

    # Crear los botones para las alternativas en la página actual
    botones = [
        {
            "type": "reply",
            "reply": {
                "id": f"button_{inicio + i + 1}",
                "title": alternativa
            }
        } for i, alternativa in enumerate(opciones_pagina_actual)
    ]

    # Añadir botones de navegación
    if pagina > 0:
        botones.append({
            "type": "reply",
            "reply": {
                "id": "anterior",
                "title": "Anterior"
            }
        })

    if fin < len(alternativas_pregunta_7):
        botones.append({
            "type": "reply",
            "reply": {
                "id": "siguiente",
                "title": "Siguiente"
            }
        })

    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": mensaje_pregunta_7
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
