import http.client
import json

PAGE_ID = "421866537676248"
ACCESS_TOKEN = "EAASSqJjOXnUBO45pvZAeoZBsyFvfN2CUSHf7LPtZA1B5DvAWBZBuOI3hq2J2lkTDQ5K31rZCxcxlkOr8UDYbT1pny3VUBplGAez2IS6CrjJe8gTREiNjrZAbrYh54ugZBn2YWwF4mZACWZCO3GRa7EZCYAFTCk0f7BQ1gtr44YaZA0aZCO37dxjhi6vE17RipO4sIFUUP28qiME7UVoVP5gX21JZASSkIUF5bxMu3y5MZD"

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
