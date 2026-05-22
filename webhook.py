from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

PHONE_NUMBER_ID = "1128696106998921"
ACCESS_TOKEN = "EAAZC2SNriB8cBRgqm2aKERjWUBDpaFZCPcJlbBZBTRHI0y0IOApXAb6GnAUeIsQsxEPa152vEOC5EeGoTvhc7aqQvXYJOucWZCZCBqXVEiIhE2E465RNrWOj4TQk0iidojWY5vwfCxF7xNWloJGH0IY0AbJfGZAYXZCwfvGN7vvI5WmCQH2nYKQ5wZCJq7sSdYCZAFZAn2HhWiFh3epdjhLg03bCLl9piRXCOJN0VrAZBiBkN2VBxyMrP7ZCAgRTjsx1Sd7vGCs4wMeO3qkijJVdR5Le"
VERIFY_TOKEN = "mi_token_secreto"

def enviar_mensaje(destinatario, mensaje):
    url = f"https://graph.facebook.com/v25.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "messaging_product": "whatsapp",
        "to": destinatario,
        "type": "text",
        "text": {"body": mensaje}
    }
    requests.post(url, headers=headers, json=data)

@app.route("/webhook", methods=["GET"])
def verificar_webhook():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Token inválido", 403

@app.route("/webhook", methods=["POST"])
def recibir_mensaje():
    data = request.get_json()
    try:
        mensajes = data["entry"][0]["changes"][0]["value"]["messages"]
        for mensaje in mensajes:
            numero = mensaje["from"]
            texto = mensaje["text"]["body"].lower()

            if "hola" in texto:
                respuesta = "¡Hola! ¿En qué te puedo ayudar? 😊"
            elif "precio" in texto:
                respuesta = "Nuestros precios van desde $100 hasta $500. ¿Quieres más información?"
            elif "horario" in texto:
                respuesta = "Atendemos de lunes a viernes de 9am a 6pm."
            else:
                respuesta = "Gracias por tu mensaje. En breve te atendemos."

            enviar_mensaje(numero, respuesta)
    except Exception as e:
        print("Error:", e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
