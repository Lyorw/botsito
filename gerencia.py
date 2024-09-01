from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import obtener_nombres_gerencia

def manejar_usuario_registrado(numero, texto_usuario, estado_usuario):
    estado = estado_usuario.get(numero, {})

    if not estado.get("mensaje_inicial_enviado", False):
        nombres_gerencia = obtener_nombres_gerencia()
        if nombres_gerencia:
            mensaje = "Perfecto, para poder ayudarte ingresa el número de tu requerimiento:\n\n"
            for i, nombre in enumerate(nombres_gerencia):
                numero_icono = ""
                for digit in str(i + 1):
                    numero_icono += f"{digit}\u20E3"
                mensaje += f"{numero_icono} {nombre}\n"
            enviar_mensaje_texto(numero, mensaje)
            estado["opciones_validas"] = list(range(1, len(nombres_gerencia) + 1))
            estado["intentos"] = 0
        else:
            enviar_mensaje_texto(numero, "No se encontraron opciones disponibles. Intente más tarde.")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True
    elif estado.get("esperando_respuesta", False):
        try:
            seleccion = int(texto_usuario)
            if seleccion in estado["opciones_validas"]:
                enviar_mensaje_texto(numero, f"Has seleccionado la opción {seleccion}. Continuemos.")
                estado_usuario.pop(numero, None)  # Aquí puedes agregar lógica para continuar el flujo
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                    estado_usuario.pop(numero, None)
        except ValueError:
            estado["intentos"] += 1
            if estado["intentos"] < 2:
                enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
            else:
                enviar_mensaje_texto(numero, "Intentos fallidos, nos vemos pronto.")
                estado_usuario.pop(numero, None)

    estado_usuario[numero] = estado
