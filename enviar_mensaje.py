import http.client
import json

PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAAYAnB4BMXoBOZBT1kevOPf7XB4EidZBtRVfCZAbDVMfJVGV1GyyRN8dSL9PO1BnTAoohKxArFuBsA5rAHauu4WfVB0kGmpKrjDN2anCZAlzMIrZALivN538MGCK8E8YuM0Dbqqy7X1uXZAZBppKMOjE3GPhu5MeeZCulWZBKYgzjQPxkexFlWKRftNkYVVbLrD0ZAd6n5vMnANZCZBn18dWkk6XOb7DsCQZD"

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
