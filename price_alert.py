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

    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": message
    }

    try:
        requests.post(url, data=payload)
        print("📩 Telegram alert sent!")

    except Exception as e:
        print("Telegram error:", e)


# GET CRYPTO PRICES


def get_crypto_prices():

    coin_list = ",".join(alerts.keys())

    if not coin_list:
        return None

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_list}&vs_currencies=usd"

    try:
        response = requests.get(url)
        data = response.json()

        prices = {}

        for coin in alerts:
            prices[coin] = float(data[coin]["usd"])

        return prices

    except Exception as e:
        print("API error:", e)
        return None


# PRICE MONITORING LOOP


def monitor_prices():

    print("🚀 Price monitoring started")

    alert_state = {}

    while True:

        prices = get_crypto_prices()

        if prices is None:
            time.sleep(CHECK_INTERVAL)
            continue

        for coin in alerts:

            price = prices[coin]
            target = alerts[coin]

            if coin not in alert_state:
                alert_state[coin] = {"above": False, "below": False}

            print(f"{coin.upper()} Price: ${price}")

            if price > target and not alert_state[coin]["above"]:

                message = f"🚀 {coin.upper()} is ABOVE your target!\nPrice: ${price}"

                send_telegram_alert(message)

                alert_state[coin]["above"] = True
                alert_state[coin]["below"] = False

            elif price < target and not alert_state[coin]["below"]:

                message = f"📉 {coin.upper()} is BELOW your target!\nPrice: ${price}"

                send_telegram_alert(message)

                alert_state[coin]["below"] = True
                alert_state[coin]["above"] = False

        time.sleep(CHECK_INTERVAL)


# API ENDPOINT


@app.route("/set-alert", methods=["POST"])
def set_alert():

    data = request.json

    coin = data["coin"]
    target = float(data["target"])

    alerts[coin] = target

    print(f"Alert set: {coin} → {target}")

    return jsonify({
        "status": "success",
        "coin": coin,
        "target": target
    })


# START SERVER + BOT


if __name__ == "__main__":

    # run monitoring in background thread
    monitor_thread = Thread(target=monitor_prices)
    monitor_thread.start()

    # start flask server
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)