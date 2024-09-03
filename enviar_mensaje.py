import http.client
import json

PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBO5zUQUoLNnBwSe9RVzTdTxz7lCl5l5X30XuzPH6uhsHJrBLS5XGPZBMJxBs6pWz8dDgLk7pZCmcJ5fEdHiWJqpSZCwWjkf9lAhpFmnCeyHj7d0oLz4HT1UaOk1vjSsLal8xcfjbsUaUVHgtad4zn2Tpq0lbRHYKgr0ZBfDsDEK2eoE5woOrz0t5vl5PqZCZBYnC67hHzLSZA64Y7DwC"

def enviar_mensaje_texto(numero, mensaje_texto):
    responder_mensaje = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": numero,
        "type": "text",
        "text": {
            "body": mensaje_texto
        }
    }
    enviar_mensaje(responder_mensaje)

def enviar_mensaje(mensaje):
    conn = http.client.HTTPSConnection("graph.facebook.com")
    payload = json.dumps(mensaje)
    headers = {
        'Authorization': f'Bearer {ACCESS_TOKEN}',
        'Content-Type': 'application/json'
    }
    conn.request("POST", f"/v15.0/{PAGE_ID}/messages", payload, headers)
    res = conn.getresponse()
    data = res.read()
    print("Respuesta de Facebook API:", data.decode("utf-8"))
