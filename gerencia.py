from enviar_mensaje import enviar_mensaje_texto

def manejar_usuario_registrado(numero, texto_usuario, estado_usuario):
    estado = estado_usuario.get(numero, {})

    if not estado.get("mensaje_inicial_enviado", False):
        enviar_mensaje_texto(numero, "Hola, ¿qué tal? Veo que ya estás registrado. ¿Puede decirme en qué le puedo ayudar?")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True
    elif estado.get("esperando_respuesta", False):
        enviar_mensaje_texto(numero, "Okey, prueba completa.")
        estado_usuario.pop(numero, None)

    estado_usuario[numero] = estado
