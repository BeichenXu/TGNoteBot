import os
import json
import requests
import gspread
from flask import Flask, request
from datetime import datetime
from google.oauth2.service_account import Credentials

app = Flask(__name__)

BOT_TOKEN = "7022294426:AAE6CTpXjDQslaQs37cRXlzfREPqy444z3k"
TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

def get_price(symbol):
    try:
        res = requests.get(f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}", timeout=2)
        return round(float(res.json()["price"]), 2)
    except:
        return "N/A"

def init_sheet():
    json_data = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    info = json.loads(json_data)
    creds = Credentials.from_service_account_info(info, scopes=["https://www.googleapis.com/auth/spreadsheets"])
    client = gspread.authorize(creds)
    return client

def log_to_sheet(timestamp, message, btc, eth):
    try:
        client = init_sheet()
        sheet = client.open("TGNoteBot").sheet1
        sheet.append_row([timestamp, message, btc, eth])
    except Exception as e:
        print("Sheet write error:", e)

@app.route("/", methods=["POST"])
def telegram_webhook():
    data = request.get_json()
    if not data or "message" not in data:
        return "No message", 400

    message = data["message"]
    chat_id = message["chat"]["id"]
    user_text = message.get("text", "")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    btc = get_price("BTCUSDT")
    eth = get_price("ETHUSDT")
    reply = f"[{timestamp}] {user_text}\nBTC/USD = ${btc}\nETH/USD = ${eth}"

    requests.post(f"{TELEGRAM_API}/sendMessage", json={
        "chat_id": chat_id,
        "text": reply
    })

    log_to_sheet(timestamp, user_text, btc, eth)

    return "ok", 200

@app.route("/", methods=["GET"])
def index():
    return "Bot is running", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
