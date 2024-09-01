import time
from enviar_mensaje import enviar_mensaje_texto
from consultas_gerencia import (
    obtener_nombres_gerencia, 
    obtener_canales_por_gerencia, 
    obtener_tipos_falla_por_canal, 
    obtener_aplicaciones_por_falla, 
    obtener_fallas_por_torre, 
    obtener_torre_por_aplicacion,
    obtener_escenarios_por_falla  # Nueva función importada
)

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
            time.sleep(2)
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
                    canales = obtener_canales_por_gerencia(seleccion)
                    if canales:
                        mensaje = "Has seleccionado una Gerencia. Ahora, selecciona el canal de venta:\n"
                        for i, canal in enumerate(canales):
                            numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                            mensaje += f"{numero_icono} {canal}\n"
                        enviar_mensaje_texto(numero, mensaje)
                        estado["opciones_validas"] = list(range(1, len(canales) + 1))
                        estado["fase"] = "seleccion_canal"
                        estado["intentos"] = 0
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron canales para esta Gerencia. Intente con otra.")
                        manejar_usuario_registrado(numero, "", estado_usuario)
                
                elif estado.get("fase") == "seleccion_canal":
                    tipos_falla = obtener_tipos_falla_por_canal(seleccion)
                    if tipos_falla:
                        mensaje = "Has seleccionado un Canal de Venta. Ahora, selecciona el tipo de falla:\n"
                        for i, tipo in enumerate(tipos_falla):
                            numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                            mensaje += f"{numero_icono} {tipo}\n"
                        enviar_mensaje_texto(numero, mensaje)
                        estado["opciones_validas"] = list(range(1, len(tipos_falla) + 1))
                        estado["fase"] = "seleccion_tipo_falla"
                        estado["intentos"] = 0
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron tipos de falla para este canal. Intente con otro.")
                        manejar_usuario_registrado(numero, "", estado_usuario)
                
                elif estado.get("fase") == "seleccion_tipo_falla":
                    aplicaciones = obtener_aplicaciones_por_falla(seleccion)
                    if aplicaciones:
                        mensaje = "Has seleccionado un Tipo de Falla. Ahora, selecciona la aplicación:\n"
                        for i, app in enumerate(aplicaciones):
                            numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                            mensaje += f"{numero_icono} {app}\n"
                        enviar_mensaje_texto(numero, mensaje)
                        estado["opciones_validas"] = list(range(1, len(aplicaciones) + 1))
                        estado["fase"] = "seleccion_aplicacion"
                        estado["intentos"] = 0
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron aplicaciones para este tipo de falla. Intente con otro.")
                        manejar_usuario_registrado(numero, "", estado_usuario)
                
                elif estado.get("fase") == "seleccion_aplicacion":
                    torre_app = obtener_torre_por_aplicacion(seleccion)
                    if torre_app:
                        enviar_mensaje_texto(numero, f"La torre de app es: {torre_app}. Continuemos con la selección de fallas.")
                        time.sleep(2)
                        fallas = obtener_fallas_por_torre(seleccion)
                        if fallas:
                            mensaje = "Selecciona la falla:\n\n"
                            for i, falla in enumerate(fallas):
                                numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                                mensaje += f"{numero_icono} {falla}\n"
                            enviar_mensaje_texto(numero, mensaje)
                            estado["opciones_validas"] = list(range(1, len(fallas) + 1))
                            estado["fase"] = "seleccion_falla"
                            estado["intentos"] = 0
                        else:
                            enviar_mensaje_texto(numero, "No se encontraron fallas para esta torre. Intente con otra.")
                            manejar_usuario_registrado(numero, "", estado_usuario)
                    else:
                        enviar_mensaje_texto(numero, "No se encontró la torre de aplicación correspondiente. Intente con otra.")
                        manejar_usuario_registrado(numero, "", estado_usuario)

                elif estado.get("fase") == "seleccion_falla":
                    escenarios = obtener_escenarios_por_falla(seleccion)
                    if escenarios:
                        mensaje = "Has seleccionado una falla. Ahora, selecciona el escenario de falla:\n"
                        for i, escenario in enumerate(escenarios):
                            numero_icono = "".join(f"{digit}\u20E3" for digit in str(i + 1))
                            mensaje += f"{numero_icono} {escenario}\n"
                        enviar_mensaje_texto(numero, mensaje)
                        estado["opciones_validas"] = list(range(1, len(escenarios) + 1))
                        estado["fase"] = "seleccion_escenario_falla"
                        estado["intentos"] = 0
                    else:
                        enviar_mensaje_texto(numero, "No se encontraron escenarios para esta falla. Intente con otro.")
                        manejar_usuario_registrado(numero, "", estado_usuario)

                elif estado.get("fase") == "seleccion_escenario_falla":
                    enviar_mensaje_texto(numero, f"Has seleccionado el escenario de falla {seleccion}. Proceso completado.")
                    estado_usuario.pop(numero, None)
                    
            else:
                estado["intentos"] += 1
                if estado["intentos"] < 2:
                    enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
                else:
                    enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                    time.sleep(2)
                    estado.clear()
                    manejar_usuario_registrado(numero, "", estado_usuario)
        except ValueError:
            estado["intentos"] += 1
            if estado["intentos"] < 2:
                enviar_mensaje_texto(numero, f"Por favor, responda con un número entre 1 y {len(estado['opciones_validas'])} para seleccionar su opción. ({estado['intentos']}/2 intentos)")
            else:
                enviar_mensaje_texto(numero, "Intentos fallidos. Regresando al inicio.")
                time.sleep(2)
                estado.clear()
                manejar_usuario_registrado(numero, "", estado_usuario)

    estado_usuario[numero] = estado
