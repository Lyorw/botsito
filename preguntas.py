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

def manejar_respuesta_interactiva(reply_id, intentos):
    if reply_id == "si_button":
        return "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)", "nombre", 0
    elif reply_id == "no_button":
        return "Okey, nos vemos pronto.", None, None
    else:
        return "Opción no reconocida.", None, None

def validar_nombre_apellido(respuesta, tipo, intentos):
    if any(char.isdigit() for char in respuesta):
        intentos += 1
        if intentos >= 2:
            return "Todos los intentos son fallidos, se le redirigirá al inicio.", True, intentos
        else:
            return f"El {tipo} no debe contener números, por favor vuelva a ingresar. Intento {intentos}/2", False, intentos
    else:
        if tipo == "nombre":
            return "Gracias, ahora ¿cuáles son tus apellidos? (Por favor, solo escribe la respuesta)", "apellido", 0
        else:
            return "¡Perfecto! Gracias por proporcionar tus datos.", True, intentos
