import os
import requests
from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

BOT_TOKEN = "7022294426:AAE6CTpXjDQslaQs37cRXlzfREPqy444z3k"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_btc_price():
    try:
        res = requests.get("https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT", timeout=2)
        return round(float(res.json()["price"]), 2)
    except:
        return "N/A"

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "No message", 400

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    btc = get_btc_price()
    reply = f"[{timestamp}] {user_text}\\nBTC/USD = ${btc}"

    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
