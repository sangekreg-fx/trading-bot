# === MAIN LOOP ===

pairs = ["XAUUSD", "BTCUSD", "EURUSD", "USDJPY", "USDCAD"]

for pair in pairs:
    candle = get_latest_candle(pair)
    sentiment = get_sentiment(pair)
    signal = "Buy" if sentiment == "Bullish" else "Sell" if sentiment == "Bearish" else "Hold"

    if candle and 'close' in candle:
        price = candle['close']
    else:
        price = "N/A"
        print(f"⚠️ No candle data returned for {pair}")

    message = f"{pair} Signal: {signal}\nSentiment: {sentiment}\nPrice: {price}"
    send_whatsapp(message)
    send_gmail(f"{pair} Signal Alert", message)
    log_to_sheet(pair, signal, sentiment)
