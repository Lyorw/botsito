import http.client
import json

PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBOz3EniX02JC9u9QhS3ZBZCgHsdmF4UYPAsKIetZApKhlCGZAbnHfmAZAZCeD6AZCIcROdea8kSSpb9wZC98GZBdheZAeW7hR0BCann831LMsF8iM9VSbZA7yLTlMzckIRxI32sfVr9ZC41t2NTbMkZBSBTxIEGY74n2pR4LdLfAhVyXABVqElpFalqFjRUCx64luZCZCoelry1LB6xqBZBdlZC2oZD"

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
