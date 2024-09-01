import time
from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import obtener_nombres_gerencia, obtener_canales_por_gerencia

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
            time.sleep(2)  # Retraso de 2 segundos
            estado["opciones_validas"] = list(range(1, len(nombres_gerencia) + 1))
            estado["intentos"] = 0
            estado["fase"] = "seleccion_gerencia"
        else:
            enviar_mensaje_texto(numero, "No se encontraron opciones disponibles. Intente más tarde.")
        estado["mensaje_inicial_enviado"] = True
        estado["esperando_respuesta"] = True

    elif estado.get("esperando_respuesta", False):
        try:
            seleccion = int(texto_usuario)
            if seleccion in estado.get("opciones_validas", []):
                if estado.get("fase") == "seleccion_gerencia":
                    enviar_mensaje_texto(numero, f"Has seleccionado una Gerencia. Ahora, selecciona el canal de venta:")
                    canales = obtener_canales_por_gerencia(seleccion)
                    if canales:
                        mensaje = ""
                        for i, canal in enumerate(canales):
                            numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                            mensaje += f"{numero_icono} {canal}\n"
                        enviar_mensaje_texto(numero, mensaje)
                        estado["opciones_validas"] = list(range(1, len(canales) + 1))
                        estado["fase"] = "seleccion_canal"
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron canales para esta Gerencia. Intente con otra.")
                        manejar_usuario_registrado(numero, "", estado_usuario)
                elif estado.get("fase") == "seleccion_canal":
                    enviar_mensaje_texto(numero, f"Has seleccionado el canal {seleccion}. Continuemos.")
                    time.sleep(2)  # Retraso de 2 segundos
                    estado_usuario.pop(numero, None)
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                    time.sleep(2)  # Retraso de 2 segundos
                    estado.clear()
                    manejar_usuario_registrado(numero, "", estado_usuario)
        except ValueError:
            estado["intentos"] += 1
            if estado["intentos"] < 2:
                enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
            else:
                enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                time.sleep(2)  # Retraso de 2 segundos
                estado.clear()
                manejar_usuario_registrado(numero, "", estado_usuario)

    estado_usuario[numero] = estado
