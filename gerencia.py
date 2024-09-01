from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import obtener_nombres_gerencia, obtener_canales_por_gerencia

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
            estado["seleccion_gerencia"] = False
        else:
            enviar_mensaje_texto(numero, "No se encontraron opciones disponibles. Intente más tarde.")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True
    elif estado.get("esperando_respuesta", False):
        try:
            seleccion = int(texto_usuario)
            if seleccion in estado["opciones_validas"] and not estado.get("seleccion_gerencia"):
                estado["seleccion_gerencia"] = True
                estado["gerencia_seleccionada"] = seleccion
                canales = obtener_canales_por_gerencia(seleccion)
                if canales:
                    mensaje = "Has seleccionado una Gerencia. Ahora, selecciona el canal de venta:\n\n"
                    for i, canal in enumerate(canales):
                        numero_icono = f"{i + 1}\u20E3"
                        mensaje += f"{numero_icono} {canal}\n"
                    enviar_mensaje_texto(numero, mensaje)
                    estado["opciones_validas"] = list(range(1, len(canales) + 1))
                    estado["intentos"] = 0
                    estado["esperando_canal"] = True
                else:
                    enviar_mensaje_texto(numero, "No se encontraron canales de venta para la gerencia seleccionada.")
                    estado_usuario.pop(numero, None)
            elif estado.get("esperando_canal", False) and seleccion in estado["opciones_validas"]:
                enviar_mensaje_texto(numero, f"Has seleccionado el canal {seleccion}. Continuemos.")
                estado_usuario.pop(numero, None)  # Aquí puedes agregar lógica para continuar el flujo
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                    manejar_usuario_registrado(numero, "", estado_usuario)
        except ValueError:
            estado["intentos"] += 1
            if estado["intentos"] < 2:
                enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
            else:
                enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                manejar_usuario_registrado(numero, "", estado_usuario)

    estado_usuario[numero] = estado
