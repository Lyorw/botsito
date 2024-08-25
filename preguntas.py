# preguntas.py

# Variable to keep track of attempts
intentos = {}

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
        return "Opción no reconocida."

def validar_nombre_apellido(text, numero):
    global intentos
    if any(char.isdigit() for char in text):
        if numero in intentos:
            intentos[numero] += 1
        else:
            intentos[numero] = 1

        if intentos[numero] > 2:
            intentos[numero] = 0  # Reset attempts for this user
            return obtener_mensaje_bienvenida()
        else:
            return f"El nombre no debe contener números, por favor vuelva a ingresar. Intento {intentos[numero]}/2"
    else:
        intentos[numero] = 0  # Reset attempts on success
        return f"Gracias, ahora ¿cuáles son tus apellidos? (Por favor, solo escribe la respuesta)"
