from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

PHONE_NUMBER_ID = "1128696106998921"
ACCESS_TOKEN = "EAAZC2SNriB8cBRmZCBW0mZBnrVkBqJXH9YgkATYbULrxhDoxp7pem0SbZBq6vcJ2In7u4YGQywYi0v8uUxNFg9u5jdaXxC2urybszYIwn0tqfQ3vJmhY2d7tK8a8I93ak21fZAIsdLUqgnKAv283UQJ052b7NIwUbPt1BZAnV9buXjGvupZCORhtzBxcuapzQHet6Me6ZCVewHqtD0P9vtkIoYIZAR6iiY53EaKtM3INbOUJfLv29ZB5W2tl7rEHQB6O29PWbDisifIUZAjDBCZBIQlZB"
VERIFY_TOKEN = "mi_token_secreto"
GEMINI_API_KEY = "AIzaSyB1UqlJKFO4z6QAq854_TLxeFdOvUsrFQ8"

SISTEMA = """Eres un asistente virtual de atención al cliente. 
Responde de forma amable, clara y concisa en español.
Si no sabes algo, di que un asesor humano le contactará pronto."""

def preguntar_gemini(mensaje):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {"Content-Type": "application/json"}
    data = {
        "contents": [
            {
                "parts": [
                    {"text": f"{SISTEMA}\n\nCliente: {mensaje}"}
                ]
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    print("Respuesta completa Gemini:", result)
    if "candidates" in result:
        return result["candidates"][0]["content"]["parts"][0]["text"]
    elif "error" in result:
        print("Error Gemini:", result["error"])
        return "Lo siento, no pude procesar tu mensaje. Un asesor te contactará pronto."
    else:
        print("Respuesta inesperada:", result)
        return "Lo siento, no pude procesar tu mensaje. Un asesor te contactará pronto."

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
    response = requests.post(url, headers=headers, json=data)
    print("Respuesta envío:", response.json())

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
            texto = mensaje["text"]["body"]
            print(f"Mensaje de {numero}: {texto}")
            respuesta = preguntar_gemini(texto)
            enviar_mensaje(numero, respuesta)
    except Exception as e:
        print("Error:", e)
    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
