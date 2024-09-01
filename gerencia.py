from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import obtener_nombres_gerencia, obtener_canales_por_gerencia_id

def manejar_usuario_registrado(numero, texto_usuario, estado_usuario):
    estado = estado_usuario.get(numero, {})

    if not estado.get("mensaje_inicial_enviado", False):
        nombres_gerencia = obtener_nombres_gerencia()
        if nombres_gerencia:
            mensaje = "Perfecto, para poder ayudarte ingresa el número de tu requerimiento:\n\n"
            for i, nombre in enumerate(nombres_gerencia):
                numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                mensaje += f"{numero_icono} {nombre}\n"
            enviar_mensaje_texto(numero, mensaje)
            estado["opciones_validas"] = list(range(1, len(nombres_gerencia) + 1))
            estado["intentos"] = 0
            estado["fase"] = "seleccion_gerencia"
        else:
            enviar_mensaje_texto(numero, "No se encontraron opciones disponibles. Intente más tarde.")
            estado_usuario.pop(numero, None)  # Termina el flujo en caso de error grave
        estado["mensaje_inicial_enviado"] = True
    elif estado.get("fase") == "seleccion_gerencia":
        try:
            seleccion = int(texto_usuario)
            if seleccion in estado["opciones_validas"]:
                estado["gerencia_seleccionada"] = seleccion
                canales = obtener_canales_por_gerencia_id(seleccion)
                if canales:
                    mensaje = "Has seleccionado una Gerencia. Ahora, selecciona el canal de venta:\n\n"
                    for i, canal in enumerate(canales):
                        numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                        mensaje += f"{numero_icono} {canal}\n"
                    enviar_mensaje_texto(numero, mensaje)
                    estado["opciones_validas"] = list(range(1, len(canales) + 1))
                    estado["fase"] = "seleccion_canal"
                    estado["intentos"] = 0
                else:
                    enviar_mensaje_texto(numero, "No se encontraron canales disponibles para la Gerencia seleccionada. Intente más tarde.")
                    estado_usuario.pop(numero, None)
            else:
                manejar_intentos(estado, numero, len(estado["opciones_validas"]), estado_usuario)
        except ValueError:
            manejar_intentos(estado, numero, len(estado["opciones_validas"]), estado_usuario)
    elif estado.get("fase") == "seleccion_canal":
        try:
            seleccion = int(texto_usuario)
            if seleccion in estado["opciones_validas"]:
                enviar_mensaje_texto(numero, f"Has seleccionado el canal {seleccion}. Continuemos.")
                # Aquí puedes continuar con la lógica del siguiente paso del flujo
                estado_usuario.pop(numero, None)
            else:
                manejar_intentos(estado, numero, len(estado["opciones_validas"]), estado_usuario)
        except ValueError:
            manejar_intentos(estado, numero, len(estado["opciones_validas"]), estado_usuario)

    estado_usuario[numero] = estado

def manejar_intentos(estado, numero, max_opciones, estado_usuario):
    estado["intentos"] += 1
    if estado["intentos"] < 2:
        enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {max_opciones} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
    else:
        enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
        estado_usuario.pop(numero, None)  # Elimina el estado actual para reiniciar
        manejar_usuario_registrado(numero, "", estado_usuario)  # Llamar a la función para reiniciar desde el principio
