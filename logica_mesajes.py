import random
import string
from conexionbd import obtener_mensaje_por_id, obtener_alternativas_por_id_pregunta, verificar_usuario_registrado
from correo import enviar_correo

# Funciones de validación y generación de códigos
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

def generar_codigo_validacion():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=4))

# Función principal de manejo de mensajes
def manejar_mensajes(data, mensajes_procesados, estado_usuario, enviar_mensaje_texto):
    entry = data.get('entry', [])[0]
    changes = entry.get('changes', [])[0]
    value = changes.get('value', {})
    objeto_mensaje = value.get('messages', [])

    if objeto_mensaje:
        messages = objeto_mensaje[0]
        numero = messages.get("from", "")
        mensaje_id = messages.get("id", "")
        texto_usuario = messages.get("text", {}).get("body", "").strip().lower()

        if mensaje_id in mensajes_procesados:
            return 'Mensaje ya procesado'
        mensajes_procesados.add(mensaje_id)

        if numero not in estado_usuario:
            estado_usuario[numero] = {
                "intentos_correo": 0,
                "intentos_nombre": 0,
                "intentos_apellido": 0,
                "intentos_numero": 0,
                "intentos_codigo": 0,
                "intentos_pregunta_7": 0,
                "intentos_pregunta_8": 0,
                "intentos_codigo_validacion": 0,
                "esperando_correo": False,
                "esperando_nombre": False,
                "esperando_apellido": False,
                "esperando_numero": False,
                "esperando_codigo": False,
                "esperando_pregunta_7": False,
                "esperando_pregunta_8": False,
                "esperando_codigo_validacion": False,
                "autenticacion_confirmada": False,
                "recordatorio_enviado": False,
                "tipo_codigo": "",
                "correo": "",
                "codigo_validacion": ""
            }
            enviar_mensaje_inicial(numero, enviar_mensaje_texto)
            return 'Mensaje inicial enviado'

        if verificar_usuario_registrado(numero):
            enviar_mensaje_texto(numero, "Usuario ya está registrado")
            return 'Usuario registrado'

        # Validaciones y lógica para cada estado del usuario
        if estado_usuario[numero].get("esperando_correo", False):
            if not validar_correo(texto_usuario):
                estado_usuario[numero]["intentos_correo"] += 1
                if estado_usuario[numero]["intentos_correo"] == 1:
                    enviar_mensaje_texto(numero, "Correo inválido, por favor vuelva a ingresar. Intento 1/2")
                elif estado_usuario[numero]["intentos_correo"] == 2:
                    enviar_mensaje_texto(numero, "Correo inválido, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
            else:
                estado_usuario[numero]["correo"] = texto_usuario
                mensaje_nombre = obtener_mensaje_por_id(3)
                enviar_mensaje_texto(numero, mensaje_nombre)
                estado_usuario[numero]["intentos_nombre"] = 0
                estado_usuario[numero]["esperando_nombre"] = True
                estado_usuario[numero]["esperando_correo"] = False
            return 'Intento de correo procesado'

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
            return 'Intento de nombre procesado'

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
            return 'Intento de apellido procesado'

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
            return 'Intento de número procesado'

        if estado_usuario[numero].get("esperando_codigo", False):
            if validar_codigo(texto_usuario):
                estado_usuario[numero]["esperando_codigo"] = False
                estado_usuario[numero]["esperando_pregunta_7"] = True
                estado_usuario[numero]["tipo_codigo"] = texto_usuario[0].upper()
                
                mensaje_pregunta_7 = obtener_mensaje_por_id(7)
                alternativas_pregunta_7 = obtener_alternativas_por_id_pregunta(7)
                
                if alternativas_pregunta_7:
                    opciones = "\n".join([f"{i+1}️⃣ {alternativa}" for i, alternativa in enumerate(alternativas_pregunta_7)])
                    enviar_mensaje_texto(numero, f"{mensaje_pregunta_7}\n\n{opciones}")
                else:
                    enviar_mensaje_texto(numero, "No se encontraron alternativas para la siguiente pregunta.")
            else:
                estado_usuario[numero]["intentos_codigo"] += 1
                if estado_usuario[numero]["intentos_codigo"] == 1:
                    enviar_mensaje_texto(numero, "Código inválido, por favor vuelva a ingresar. Intento 1/2")
                elif estado_usuario[numero]["intentos_codigo"] == 2:
                    enviar_mensaje_texto(numero, "Código inválido, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
            return 'Intento de código procesado'

        if estado_usuario[numero].get("esperando_pregunta_7", False):
            tipo_codigo = estado_usuario[numero]["tipo_codigo"]
            valid_ids = []

            if tipo_codigo == "E":
                valid_ids = [4, 6, 7]
            elif tipo_codigo == "C":
                valid_ids = [3]
            elif tipo_codigo == "D":
                valid_ids = [5]

            try:
                alternativa_id = int(texto_usuario)
                id_map = {
                    1: 3,
                    2: 4,
                    3: 5,
                    4: 6,
                    5: 7
                }
                if id_map.get(alternativa_id) in valid_ids:
                    enviar_mensaje_texto(numero, "Gracias, puede proceder.")
                    estado_usuario[numero]["esperando_pregunta_7"] = False
                    estado_usuario[numero]["esperando_pregunta_8"] = True
                    mensaje_pregunta_8 = obtener_mensaje_por_id(8)
                    alternativas_pregunta_8 = obtener_alternativas_por_id_pregunta(8)
                    if alternativas_pregunta_8:
                        opciones = "\n".join([f"{i+1}️⃣ {alternativa}" for i, alternativa in enumerate(alternativas_pregunta_8)])
                        enviar_mensaje_texto(numero, f"{mensaje_pregunta_8}\n\n{opciones}")
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron alternativas para la siguiente pregunta.")
                else:
                    estado_usuario[numero]["intentos_pregunta_7"] += 1
                    if estado_usuario[numero]["intentos_pregunta_7"] == 1:
                        enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 5 para seleccionar su canal donde corresponda. (1/2 intentos)")
                    elif estado_usuario[numero]["intentos_pregunta_7"] == 2:
                        enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
            except ValueError:
                estado_usuario[numero]["intentos_pregunta_7"] += 1
                if estado_usuario[numero]["intentos_pregunta_7"] == 1:
                    enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 5 para seleccionar su canal donde corresponda. (1/2 intentos)")
                elif estado_usuario[numero]["intentos_pregunta_7"] == 2:
                    enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
            return 'Respuesta a pregunta 7 procesada'

        if estado_usuario[numero].get("esperando_pregunta_8", False):
            try:
                alternativa_id = int(texto_usuario)
                if 1 <= alternativa_id <= 4:
                    codigo_validacion = generar_codigo_validacion()
                    estado_usuario[numero]["codigo_validacion"] = codigo_validacion
                    enviar_correo(estado_usuario[numero]["correo"], codigo_validacion)

                    estado_usuario[numero]["esperando_codigo_validacion"] = True
                    estado_usuario[numero]["intentos_codigo_validacion"] = 0
                    enviar_mensaje_texto(numero, "Se envió a su correo un código de validación, ingrese el código para finalizar.")
                    estado_usuario[numero]["esperando_pregunta_8"] = False
                else:
                    estado_usuario[numero]["intentos_pregunta_8"] += 1
                    if estado_usuario[numero]["intentos_pregunta_8"] == 1:
                        enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 4 para seleccionar su opción. (1/2 intentos)")
                    elif estado_usuario[numero]["intentos_pregunta_8"] == 2:
                        enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                        estado_usuario.pop(numero, None)
            except ValueError:
                estado_usuario[numero]["intentos_pregunta_8"] += 1
                if estado_usuario[numero]["intentos_pregunta_8"] == 1:
                    enviar_mensaje_texto(numero, "Por favor, responda con un número entre 1 y 4 para seleccionar su opción. (1/2 intentos)")
                elif estado_usuario[numero]["intentos_pregunta_8"] == 2:
                    enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
            return 'Respuesta a pregunta 8 procesada'

        if estado_usuario[numero].get("esperando_codigo_validacion", False):
            if texto_usuario == estado_usuario[numero]["codigo_validacion"]:
                enviar_mensaje_texto(numero, "¡Felicidades! Su proceso de autenticación ha sido completado con éxito.")
                estado_usuario.pop(numero, None)
            else:
                estado_usuario[numero]["intentos_codigo_validacion"] += 1
                if estado_usuario[numero]["intentos_codigo_validacion"] == 1:
                    enviar_mensaje_texto(numero, "Código incorrecto, por favor intente nuevamente. Intento 1/2")
                elif estado_usuario[numero]["intentos_codigo_validacion"] == 2:
                    enviar_mensaje_texto(numero, "Código incorrecto. Intentos fallidos, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
            return 'Validación de código procesada'

    return 'No hay mensajes para procesar'

def validar_correo(correo):
    patron = r'^[A-Za-z]{5,}@(globalhitss\.com|claro\.com\.pe)$'
    return re.match(patron, correo) is not None

def enviar_mensaje_inicial(numero, enviar_mensaje_texto):
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
    enviar_mensaje_texto(numero, responder_mensaje)
