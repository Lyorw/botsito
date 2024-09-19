from flask import Flask, request, jsonify
import http.client
import json

app = Flask(__name__)

# Lista para almacenar los mensajes recibidos temporalmente
mensajes_recibidos = []

@app.route('/webhook', methods=['GET'])
def verificar_token():
    """Verificar el token con el token de Meta para validar el webhook."""
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')

    # Asumimos que el VERIFY_TOKEN se puede pasar como parte de la URL en la configuración de Meta
    verify_token_local = "ANDERCODE"

    if challenge and token == verify_token_local:
        return challenge
    else:
        return jsonify({'error': 'Token Inválido'}), 401

@app.route('/webhook', methods=['POST'])
def recibir_mensajes():
    """Recibir y procesar mensajes entrantes desde WhatsApp."""
    try:
        data = request.get_json()
        print("Data received:", json.dumps(data, indent=2))  # Imprimir los datos completos recibidos

        # Extraer la información del mensaje
        entry = data.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})
        objeto_mensaje = value.get('messages', [])

        if objeto_mensaje:
            messages = objeto_mensaje[0]
            numero = messages.get("from", "")
            texto_usuario = messages.get("text", {}).get("body", "").strip()
            
            # Almacenar el mensaje recibido
            mensajes_recibidos.append({'numero': numero, 'mensaje': texto_usuario})
            
            # Imprimir el mensaje recibido y el número
            print(f"Mensaje recibido de {numero}: {texto_usuario}")

            return jsonify({'status': 'Mensaje recibido y registrado'}), 200
        else:
            return jsonify({'error': 'No hay mensajes para procesar'}), 400
    except Exception as e:
        print("Error en el procesamiento del mensaje:", e)
        return jsonify({'error': 'Error en el procesamiento del mensaje'}), 500

@app.route('/get-mensajes', methods=['GET'])
def obtener_mensajes():
    """Devuelve todos los mensajes recibidos sin limpiar la memoria."""
    return jsonify(mensajes_recibidos), 200

@app.route('/clear-mensajes', methods=['POST'])
def limpiar_mensajes():
    """Limpia todos los mensajes almacenados."""
    mensajes_recibidos.clear()
    return jsonify({'status': 'Mensajes limpiados'}), 200

@app.route('/send-message', methods=['POST'])
def send_message():
    data = request.get_json()
    numero = data.get('numero')
    mensaje_texto = data.get('mensaje_texto')
    
    # Recibir credenciales desde el código local
    access_token = data.get('access_token')
    page_id = data.get('page_id')

    # Imprimir los datos recibidos para depuración
    print(f"Datos recibidos - Número: {numero}, Mensaje: {mensaje_texto}")

    if not numero or not mensaje_texto:
        return jsonify({'error': 'Falta el número o el mensaje'}), 400

    try:
        enviar_mensaje_texto(numero, mensaje_texto, access_token, page_id)
        return jsonify({'status': 'Mensaje enviado'}), 200
    except Exception as e:
        print(f"Error al enviar mensaje: {str(e)}")  # Añadir impresión para depuración
        return jsonify({'error': str(e)}), 500

def enviar_mensaje_texto(numero, mensaje_texto, access_token, page_id):
    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje_texto
        }
    }
    enviar_mensaje(responder_mensaje, access_token, page_id)

def enviar_mensaje(mensaje, access_token, page_id):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload = json.dumps(mensaje)
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    conn.request("POST", f"/v15.0/{page_id}/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()
    
    # Imprimir la respuesta del API de Facebook para depuración
    print("Respuesta de Facebook API:", data.decode("utf-8"))

if __name__ == '__main__':
    # Verificar la conexión con el API de Meta al iniciar el servidor (opcional)
    # verificar_conexion_meta()
    app.run(host='0.0.0.0', port=80)
