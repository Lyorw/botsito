# preguntas.py

# Define estados para el flujo de conversación
ESTADOS = {
    "INICIO": "inicio",
    "NOMBRE": "nombre",
    "APELLIDO": "apellido",
    "FINAL": "final"
}

def inicializar_estado_usuario():
    return {"estado": ESTADOS["INICIO"], "intentos": 0}

def cambiar_estado_usuario(usuario_estado, nuevo_estado):
    usuario_estado["estado"] = nuevo_estado

def obtener_mensaje_bienvenida():
    return {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "type": "interactive",
        "interactive": {
            "type": "button",
            "body": {
                "text": "😊 ¡Hola! Bienvenido/a a nuestro chatbot de autenticación. Estoy aquí para ayudarte a completar el proceso de manera rápida y segura. Antes de comenzar, ¿estás de acuerdo en llevar a cabo este proceso de autenticación? Por favor, responde con 'Sí' para continuar o 'No' si prefieres no seguir adelante."
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

def manejar_respuesta_interactiva(reply_id, usuario_estado):
    estado_actual = usuario_estado.get("estado", ESTADOS["INICIO"])
    print(f"Estado actual: {estado_actual}")  # Mensaje de depuración

    if estado_actual == ESTADOS["INICIO"]:
        if reply_id == "si_button":
            cambiar_estado_usuario(usuario_estado, ESTADOS["NOMBRE"])
            return "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)"
        elif reply_id == "no_button":
            return "Okey, nos vemos pronto."
        else:
            return "Opción no reconocida. Por favor, responde con 'Sí' o 'No'."
    
    elif estado_actual == ESTADOS["NOMBRE"]:
        return validar_nombre_apellido(reply_id, usuario_estado, "nombre")
    
    elif estado_actual == ESTADOS["APELLIDO"]:
        return validar_nombre_apellido(reply_id, usuario_estado, "apellido")
    
    elif estado_actual == ESTADOS["FINAL"]:
        return "¡Gracias por completar el formulario!"
    
    return "Estado no reconocido."

def validar_nombre_apellido(input_text, usuario_estado, tipo):
    print(f"Validando {tipo}: {input_text}")  # Mensaje de depuración
    
    if any(char.isdigit() for char in input_text):
        intentos = usuario_estado.get("intentos", 0) + 1
        usuario_estado["intentos"] = intentos
        
        if intentos < 2:
            return f"El {tipo} no debe contener números. Por favor, vuelva a ingresar. Intento {intentos}/2.", False
        else:
            cambiar_estado_usuario(usuario_estado, ESTADOS["INICIO"])  # Redirige al inicio después de fallar
            return "Todos los intentos han fallado. Se le redirigirá al inicio.", True
    else:
        if tipo == "nombre":
            cambiar_estado_usuario(usuario_estado, ESTADOS["APELLIDO"])
            return "Gracias, ahora ¿cuáles son tus apellidos? (Por favor, solo escribe la respuesta).", True
        elif tipo == "apellido":
            cambiar_estado_usuario(usuario_estado, ESTADOS["FINAL"])
            return "¡Perfecto! Gracias por completar el formulario.", True
