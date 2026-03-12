# Crypto Price Alert Telegram Bot

A Python automation bot that monitors cryptocurrency prices and sends alerts via Telegram when prices go above or below a target value.

## Features

- Tracks multiple cryptocurrencies
- Sends real-time alerts to Telegram
- Prevents duplicate alerts
- Runs automatically in a loop
- Uses CoinGecko API for price data

## Deployment
This bot is deployed on Railway and runs 24/7

## Technologies Used

- Python
- Requests Library
- Telegram Bot API
- CoinGecko API
- Railway Cloud Hosting

## Installation

Clone the repository:

git clone https://github.com/yourusername/crypto-alert-bot.git

Navigate into the project folder:

cd crypto-alert-bot

Install dependencies:

pip install -r requirements.txt

## Setup

Create a `.env` file in the project root and add:

TOKEN=your_telegram_bot_token
CHAT_ID=your_chat_id

## Run the Bot

Run the script with:

python bot.py

The bot will check cryptocurrency prices every 60 seconds and send alerts to Telegram if the price crosses the target threshold.

## Example Alert

🚀 BITCOIN is ABOVE your target  
Price: $70250

## Author

Divine Eyaja
