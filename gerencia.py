# gestion_usuarios.py

from app import enviar_mensaje_texto

# Función para manejar la conversación con usuarios registrados
def manejar_usuario_registrado(numero, texto_usuario, estado_usuario):
    estado = estado_usuario.get(numero, {})

    # Verificar si el usuario ya ha recibido el mensaje inicial
    if not estado.get("mensaje_inicial_enviado", False):
        enviar_mensaje_texto(numero, "Hola, ¿qué tal? Veo que ya estás registrado. ¿Puede decirme en qué le puedo ayudar?")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True
    elif estado.get("esperando_respuesta", False):
        # Aquí simplemente respondemos para validar la función
        enviar_mensaje_texto(numero, "Okey, prueba completa.")
        estado_usuario.pop(numero, None)  # Limpiamos el estado del usuario después de responder

    estado_usuario[numero] = estado
