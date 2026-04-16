from flask import Flask, request
import requests
from google.cloud import dialogflow_v2 as dialogflow
import os

app = Flask(__name__)

# 🔑 SET THESE
PAGE_ACCESS_TOKEN = "PASTE_YOUR_FACEBOOK_PAGE_TOKEN"
VERIFY_TOKEN = "my_verify_token"
PROJECT_ID = "PASTE_YOUR_DIALOGFLOW_PROJECT_ID"

# Dialogflow response
def detect_intent(text, session_id):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(PROJECT_ID, session_id)

    text_input = dialogflow.TextInput(text=text, language_code="en")
    query_input = dialogflow.QueryInput(text=text_input)

    response = session_client.detect_intent(
        request={"session": session, "query_input": query_input}
    )

    return response.query_result.fulfillment_text

# Send reply to Messenger
def send_message(recipient_id, text):
    url = "https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    requests.post(url, params=params, json=data)

# 🔐 Verification (IMPORTANT)
@app.route('/webhook', methods=['GET'])
def verify():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if token == VERIFY_TOKEN:
        return challenge
    return "Verification failed"

# 📩 Receive messages
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    for entry in data.get("entry", []):
        for msg in entry.get("messaging", []):
            sender_id = msg["sender"]["id"]

            if "message" in msg:
                text = msg["message"].get("text", "")

                reply = detect_intent(text, sender_id)
                send_message(sender_id, reply)

    return "ok", 200

if __name__ == "__main__":
    app.run(port=5000)