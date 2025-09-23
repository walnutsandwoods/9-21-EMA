import yfinance as yf
import pandas as pd
import schedule
import time
import asyncio
from datetime import time as dt_time
import pytz

# Import alert functions from the new alerts module
from alerts import read_config, send_telegram_alert

# --- Configuration ---
STOCK_LIST_FILE = 'nifty500.txt'
TIMEZONE = pytz.timezone('Asia/Kolkata')
MARKET_START_TIME = dt_time(9, 15)
MARKET_END_TIME = dt_time(15, 30)
SCAN_INTERVAL_MINUTES = 10

def read_stock_symbols():
    """Reads stock symbols from the specified file."""
    try:
        with open(STOCK_LIST_FILE, 'r') as f:
            symbols_str = f.read()
            # Append .NS to each symbol for Yahoo Finance
            symbols = [symbol.strip() + ".NS" for symbol in symbols_str.split(',') if symbol.strip()]
            return symbols
    except FileNotFoundError:
        print(f"Error: Stock list file '{STOCK_LIST_FILE}' not found.")
        return []

def scan_for_crossovers(symbols, bot_token, chat_id):
    """Scans for EMA crossovers and sends alerts."""
    print(f"\n--- Running scanner at {pd.Timestamp.now(tz=TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} ---")
    if not symbols:
        print("No symbols to scan.")
        return

    try:
        # Fetch data for all stocks at once. Period needs to be at least 2 days to get previous day's close
        data = yf.download(symbols, period="60d", progress=False)
        if data.empty:
            print("Could not download any stock data.")
            return
    except Exception as e:
        print(f"Failed to download stock data: {e}")
        return

    bullish_crossovers = []
    bearish_crossovers = []

    for symbol in symbols:
        try:
            # Extract close prices for the symbol
            close_prices = data['Close'][symbol].dropna()

            if len(close_prices) < 22: # Need enough data for 21-day EMA
                continue

            # Calculate EMAs
            ema9 = close_prices.ewm(span=9, adjust=False).mean()
            ema21 = close_prices.ewm(span=21, adjust=False).mean()

            # Get the last two values
            prev_ema9 = ema9.iloc[-2]
            curr_ema9 = ema9.iloc[-1]
            prev_ema21 = ema21.iloc[-2]
            curr_ema21 = ema21.iloc[-1]

            # Check for NaN values
            if any(pd.isna(v) for v in [prev_ema9, curr_ema9, prev_ema21, curr_ema21]):
                continue

            # --- Bullish Crossover ---
            # Was below, now above
            if prev_ema9 <= prev_ema21 and curr_ema9 > curr_ema21:
                # We also need to check the original condition: open > 9ema
                latest_open = data['Open'][symbol].iloc[-1]
                if pd.notna(latest_open) and latest_open > curr_ema9:
                    bullish_crossovers.append(symbol)

            # --- Bearish Crossover ---
            # Was above, now below
            if prev_ema9 >= prev_ema21 and curr_ema9 < curr_ema21:
                # We also need to check the original condition: open < 9ema
                latest_open = data['Open'][symbol].iloc[-1]
                if pd.notna(latest_open) and latest_open < curr_ema9:
                    bearish_crossovers.append(symbol)

        except KeyError:
            # This can happen if a symbol fails to download
            pass
        except Exception as e:
            print(f"Could not process {symbol}: {e}")

    # Send alerts
    if bullish_crossovers:
        message = "📈 Bullish Crossover Alert:\n" + "\n".join(bullish_crossovers)
        # We need to use asyncio.run() to call the async function from our sync code
        asyncio.run(send_telegram_alert(bot_token, chat_id, message))

    if bearish_crossovers:
        message = "📉 Bearish Crossover Alert:\n" + "\n".join(bearish_crossovers)
        asyncio.run(send_telegram_alert(bot_token, chat_id, message))

    if not bullish_crossovers and not bearish_crossovers:
        print("No new crossovers found.")

def main():
    """Main function to run the scanner."""
    bot_token, chat_id = read_config()
    if not bot_token or not chat_id:
        return

    symbols = read_stock_symbols()
    if not symbols:
        return

    print("--- Stock Scanner Initialized ---")
    print(f"Scanning {len(symbols)} stocks from '{STOCK_LIST_FILE}'.")
    print(f"Alerts will be sent via Telegram.")
    print(f"Scanner will run every {SCAN_INTERVAL_MINUTES} minutes during market hours.")

    # Schedule the job
    schedule.every(SCAN_INTERVAL_MINUTES).minutes.do(
        lambda: scan_for_crossovers(symbols, bot_token, chat_id)
    )

    # Initial run
    scan_for_crossovers(symbols, bot_token, chat_id)

    # Main loop to run the scheduler
    while True:
        now = pd.Timestamp.now(tz=TIMEZONE)
        if now.weekday() < 5 and MARKET_START_TIME <= now.time() <= MARKET_END_TIME:
            schedule.run_pending()
        time.sleep(60) # Sleep for 1 minute

if __name__ == "__main__":
    main()
