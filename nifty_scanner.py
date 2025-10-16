# nifty_scanner.py
import yfinance as yf
import pandas as pd
import time
import os
import asyncio
from datetime import time as dt_time
import pytz
from dotenv import load_dotenv

# Import from our new alerts module
from alerts import send_telegram_alert, send_telegram_alert_sync, get_telegram_config

# Load environment variables
load_dotenv()

# --- Configuration ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
STOCK_LIST_FILE = os.path.join(SCRIPT_DIR, 'nifty500.txt')
TIMEZONE = pytz.timezone('Asia/Kolkata')
MARKET_START_TIME = dt_time(9, 15)
MARKET_END_TIME = dt_time(15, 30)
SCAN_INTERVAL_MINUTES = 10
BATCH_SIZE = 50

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

def scan_for_crossovers(symbols):
    """Scans for EMA crossovers on 1-hour timeframe and sends alerts."""
    print(f"\n--- Running scanner at {pd.Timestamp.now(tz=TIMEZONE).strftime('%Y-%m-%d %H:%M:%S')} ---")
    if not symbols:
        print("No symbols to scan.")
        return

    bullish_crossovers = []
    bearish_crossovers = []
    total_symbols = len(symbols)
    num_batches = (total_symbols + BATCH_SIZE - 1) // BATCH_SIZE

    for i in range(0, total_symbols, BATCH_SIZE):
        batch_symbols = symbols[i:i + BATCH_SIZE]
        print(f"--- Processing batch {i//BATCH_SIZE + 1}/{num_batches} ({len(batch_symbols)} symbols) ---")

        try:
            # Fetch 1-hour data for the current batch (1 month of 1-hour data)
            data = yf.download(batch_symbols, period="1mo", interval="1h", progress=False, auto_adjust=True)
            if data.empty:
                print("Could not download any stock data for this batch.")
                continue
        except Exception as e:
            print(f"Failed to download stock data for this batch: {e}")
            continue

        for symbol in batch_symbols:
            try:
                # Extract close prices for the symbol
                close_prices = data['Close'][symbol].dropna()

                if len(close_prices) < 22:  # Need enough data for 21-period EMA
                    continue

                # Calculate EMAs on 1-hour data
                ema9 = close_prices.ewm(span=9, adjust=False).mean()
                ema21 = close_prices.ewm(span=21, adjust=False).mean()

                # Get the last two values (current and previous candle)
                prev_ema9, curr_ema9 = ema9.iloc[-2], ema9.iloc[-1]
                prev_ema21, curr_ema21 = ema21.iloc[-2], ema21.iloc[-1]

                # Check for NaN values
                if any(pd.isna(v) for v in [prev_ema9, curr_ema9, prev_ema21, curr_ema21]):
                    continue

                # --- Bullish Crossover ---
                # Was below, now above (on 1-hour timeframe)
                if prev_ema9 <= prev_ema21 and curr_ema9 > curr_ema21:
                    latest_open = data['Open'][symbol].iloc[-1]
                    if pd.notna(latest_open) and latest_open > curr_ema9:
                        stock_name = symbol.replace('.NS', '')
                        bullish_crossovers.append(stock_name)
                        print(f"  🟢 BULLISH: {stock_name}")

                # --- Bearish Crossover ---
                # Was above, now below (on 1-hour timeframe)
                if prev_ema9 >= prev_ema21 and curr_ema9 < curr_ema21:
                    latest_open = data['Open'][symbol].iloc[-1]
                    if pd.notna(latest_open) and latest_open < curr_ema9:
                        stock_name = symbol.replace('.NS', '')
                        bearish_crossovers.append(stock_name)
                        print(f"  🔴 BEARISH: {stock_name}")

            except KeyError:
                pass  # Symbol not in downloaded data
            except Exception as e:
                print(f"Could not process {symbol}: {e}")

    # Send alerts after processing all batches
    print("\n--- Scan complete. Sending alerts... ---")
    
    if bullish_crossovers:
        message = "📈 1-Hour Bullish EMA Crossover:\n" + "\n".join(f"• {stock}" for stock in bullish_crossovers)
        send_telegram_alert_sync(message)

    if bearish_crossovers:
        message = "📉 1-Hour Bearish EMA Crossover:\n" + "\n".join(f"• {stock}" for stock in bearish_crossovers)
        send_telegram_alert_sync(message)

    if not bullish_crossovers and not bearish_crossovers:
        print("No new crossovers found on 1-hour timeframe.")

def main():
    """Main function to run the scanner."""
    # Test Telegram configuration first
    bot_token, chat_id = get_telegram_config()
    if not bot_token or not chat_id:
        print("Telegram configuration failed. Please check your .env file.")
        return

    symbols = read_stock_symbols()
    if not symbols:
        return

    print("--- 1-Hour EMA Scanner Initialized ---")
    print(f"Scanning {len(symbols)} stocks from '{STOCK_LIST_FILE}'.")
    print(f"Timeframe: 1-Hour | EMAs: 9/21")
    print(f"Alerts will be sent via Telegram.")
    print(f"Scanner will run every {SCAN_INTERVAL_MINUTES} minutes during market hours.")
    
    # Send startup message
    send_telegram_alert_sync("🔄 1-Hour EMA Scanner Started - Monitoring 500 stocks for 9/21 crossovers")

    # Main loop
    while True:
        now = pd.Timestamp.now(tz=TIMEZONE)
        
        # Check if it's market hours on a weekday
        if now.weekday() < 5 and MARKET_START_TIME <= now.time() <= MARKET_END_TIME:
            print(f"Market hours detected. Running scan at {now.strftime('%H:%M:%S')}")
            scan_for_crossovers(symbols)
        else:
            print(f"Outside market hours: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Wait for the specified interval
        time.sleep(SCAN_INTERVAL_MINUTES * 60)

if __name__ == "__main__":
    main()
