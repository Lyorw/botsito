from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import obtener_nombres_gerencia

def manejar_usuario_registrado(numero, texto_usuario, estado_usuario):
    estado = estado_usuario.get(numero, {})

    if not estado.get("mensaje_inicial_enviado", False):
        nombres_gerencia = obtener_nombres_gerencia()
        if nombres_gerencia:
            mensaje = "Perfecto, para poder ayudarte ingresa el número de tu requerimiento:\n\n"
            for i, nombre in enumerate(nombres_gerencia):
                if i < 9:
                    mensaje += f"{i+1}\u20E3 {nombre}\n"  # Icono numérico para 1-9
                else:
                    mensaje += f"{i+1}. {nombre}\n"  # Número con punto para 10 en adelante
            enviar_mensaje_texto(numero, mensaje)
        else:
            enviar_mensaje_texto(numero, "No se encontraron opciones disponibles. Intente más tarde.")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True
    elif estado.get("esperando_respuesta", False):
        enviar_mensaje_texto(numero, "Okey, prueba completa.")
        estado_usuario.pop(numero, None)

    estado_usuario[numero] = estado
