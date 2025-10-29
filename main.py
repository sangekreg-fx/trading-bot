# main.py
import requests
from twilio.rest import Client
import smtplib
from email.mime.text import MIMEText
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# === CONFIG ===
TWELVE_DATA_API_KEY = "d3732b20faae4551b72df75bf3d6ffd1"
FINNHUB_API_KEY = "d40v3ahr01qhkm8b1lrgd40v3ahr01qhkm8b1ls0"

TWILIO_SID = "ACc71a1cfeda69b90707a8fdf0806da159"
TWILIO_AUTH_TOKEN = "08888e163f2820f54e3953d8a7d6c27f"
TWILIO_WHATSAPP_FROM = "whatsapp:+14155238886"
WHATSAPP_TO = "whatsapp:+256752721686"

GMAIL_USER = "jacobtimba0@gmail.com"
GMAIL_PASSWORD = "BoB5/01/2007"
GMAIL_TO = "jacobtimba0@gmail.com"

GOOGLE_SHEET_NAME = "Trading Signals"
GOOGLE_CREDENTIALS_FILE = "credentials.json"

# === FUNCTIONS ===

def get_latest_candle(symbol):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=1h&apikey={TWELVE_DATA_API_KEY}&outputsize=1"
    response = requests.get(url).json()
    if "values" in response:
        return response["values"][0]
    return None

def get_sentiment(symbol):
    url = f"https://finnhub.io/api/v1/news?category=forex&token={FINNHUB_API_KEY}"
    response = requests.get(url).json()
    headlines = [item["headline"] for item in response if symbol in item["headline"]]
    score = sum("bullish" in h.lower() for h in headlines) - sum("bearish" in h.lower() for h in headlines)
    return "Bullish" if score > 0 else "Bearish" if score < 0 else "Neutral"

def send_whatsapp(message):
    client = Client(TWILIO_SID, TWILIO_AUTH_TOKEN)
    client.messages.create(body=message, from_=TWILIO_WHATSAPP_FROM, to=WHATSAPP_TO)

def send_gmail(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = GMAIL_TO
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(GMAIL_USER, GMAIL_PASSWORD)
    server.sendmail(GMAIL_USER, GMAIL_TO, msg.as_string())
    server.quit()

def log_to_sheet(pair, signal, sentiment):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
    client = gspread.authorize(creds)
    sheet = client.open(GOOGLE_SHEET_NAME).sheet1
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([pair, signal, sentiment, timestamp])

# === MAIN LOOP ===

pairs = ["XAUUSD", "BTCUSD", "EURUSD", "USDJPY", "USDCAD"]

for pair in pairs:
    candle = get_latest_candle(pair)
    sentiment = get_sentiment(pair)
    signal = "Buy" if sentiment == "Bullish" else "Sell" if sentiment == "Bearish" else "Hold"

    message = f"{pair} Signal: {signal}\nSentiment: {sentiment}\nPrice: {candle['close']}"
    send_whatsapp(message)
    send_gmail(f"{pair} Signal Alert", message)
    log_to_sheet(pair, signal, sentiment)
