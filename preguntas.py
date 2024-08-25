# preguntas.py

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

def manejar_respuesta_interactiva(reply_id):
    if reply_id == "si_button":
        return "😊 Para comenzar, ¿puedes decirme tu nombre completo? (Por favor, solo escribe la respuesta)"
    elif reply_id == "no_button":
        return "Okey, nos vemos pronto."
    else:
        return "Opción no reconocida. Por favor, responde con 'Sí' o 'No'."

def validar_nombre_apellido(input_text, intentos, tipo):
    if any(char.isdigit() for char in input_text):
        if intentos < 2:
            return f"El {tipo} no debe contener números. Por favor, vuelva a ingresar. Intento {intentos}/2.", False
        else:
            return "Todos los intentos han fallado. Se le redirigirá al inicio.", True
    else:
        if tipo == "nombre":
            return "Gracias, ahora ¿cuáles son tus apellidos? (Por favor, solo escribe la respuesta).", True
        elif tipo == "apellido":
            return "¡Perfecto! Gracias por completar el formulario.", True
