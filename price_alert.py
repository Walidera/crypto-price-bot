import requests
import time
import os
from dotenv import load_dotenv


# CONFIGURATION

load_dotenv()

TOKEN = os.getenv("TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

CHECK_INTERVAL = 60  # seconds

coins = {
    "bitcoin": 70500,
    "ethereum": 2020,
    "solana": 85
}


# TELEGRAM FUNCTION


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

    coin_list = ",".join(coins.keys())

    url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_list}&vs_currencies=usd"

    try:
        response = requests.get(url)
        data = response.json()

        prices = {}

        for coin in coins:
            prices[coin] = float(data[coin]["usd"])

        return prices

    except Exception as e:
        print("API error:", e)
        return None

# MAIN BOT LOOP


alerts = {coin: {"above": False, "below": False} for coin in coins}

def run_bot():

    print("🚀 Crypto Price Bot Started")

    while True:

        prices = get_crypto_prices()

        if prices is None:
            time.sleep(CHECK_INTERVAL)
            continue

        for coin in coins:

            price = prices[coin]
            target = coins[coin]

            print(f"{coin.upper()} Price: ${price}")

            if price > target and not alerts[coin]["above"]:

                message = f"🚀 {coin.upper()} is ABOVE your target!\nPrice: ${price}"

                send_telegram_alert(message)

                alerts[coin]["above"] = True
                alerts[coin]["below"] = False

            elif price < target and not alerts[coin]["below"]:

                message = f"📉 {coin.upper()} is BELOW your target!\nPrice: ${price}"

                send_telegram_alert(message)

                alerts[coin]["below"] = True
                alerts[coin]["above"] = False

        time.sleep(CHECK_INTERVAL)


# START BOT

if __name__ == "__main__":
    run_bot()
