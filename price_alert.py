import requests
import time
import os
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from threading import Thread

# LOAD ENV VARIABLES
load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 60

# FLASK APP
app = Flask(__name__)

# store alert targets
alerts = {}

# TELEGRAM ALERT FUNCTION
def send_telegram_alert(message):
    if not TOKEN or not CHAT_ID:
        print("❌ Missing TOKEN or CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        response = requests.post(url, data=payload, timeout=10)
        print("📩 Telegram alert sent!", response.status_code)
    except Exception as e:
        print("Telegram error:", e)


# GET CRYPTO PRICES
def get_crypto_prices():
    coin_list = ",".join(alerts.keys())

    if not coin_list:
        return None

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_list}&vs_currencies=usd"

    try:
        response = requests.get(url, timeout=10)
        data = response.json()

        prices = {}

        for coin in alerts:
            if coin in data:
                prices[coin] = float(data[coin]["usd"])
            else:
                print(f"⚠️ Coin not found: {coin}")

        return prices

    except Exception as e:
        print("API error:", e)
        return None


# PRICE MONITORING LOOP
def monitor_prices():
    print("🚀 Price monitoring started")

    alert_state = {}

    while True:
        try:
            prices = get_crypto_prices()

            if prices is None:
                time.sleep(CHECK_INTERVAL)
                continue

            for coin in alerts:
                if coin not in prices:
                    continue

                price = prices[coin]
                target = alerts[coin]

                if coin not in alert_state:
                    alert_state[coin] = {"above": False, "below": False}

                print(f"{coin.upper()} Price: ${price}")

                if price > target and not alert_state[coin]["above"]:
                    message = f"🚀 {coin.upper()} ABOVE target!\nPrice: ${price}"
                    send_telegram_alert(message)

                    alert_state[coin]["above"] = True
                    alert_state[coin]["below"] = False

                elif price < target and not alert_state[coin]["below"]:
                    message = f"📉 {coin.upper()} BELOW target!\nPrice: ${price}"
                    send_telegram_alert(message)

                    alert_state[coin]["below"] = True
                    alert_state[coin]["above"] = False

            time.sleep(CHECK_INTERVAL)

        except Exception as e:
            print("🔥 Monitor crash prevented:", e)
            time.sleep(10)


# ROOT ROUTE FOR RAILWAY

@app.route("/")
def home():
    return "Crypto Bot is running 🚀"


# API ENDPOINT
@app.route("/set-alert", methods=["POST"])
def set_alert():
    try:
        data = request.get_json()

        coin = data["coin"].lower()
        target = float(data["target"])

        alerts[coin] = target

        print(f"Alert set: {coin} → {target}")

        return jsonify({
            "status": "success",
            "coin": coin,
            "target": target
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# START SERVER + BOT
if __name__ == "__main__":

    def start_bot():
        monitor_prices()

    monitor_thread = Thread(target=start_bot)
    monitor_thread.daemon = True  # 🔥 prevents Railway crash
    monitor_thread.start()

    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)