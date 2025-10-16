# app.py
import streamlit as st
from nifty_scanner import scan_for_crossovers, read_stock_symbols
from alerts import send_telegram_alert_sync
import pandas as pd
import pytz
from datetime import time as dt_time

# Initialize session state for last run time
if 'last_run' not in st.session_state:
    st.session_state.last_run = None

# Configuration
TIMEZONE = pytz.timezone('Asia/Kolkata')
MARKET_START_TIME = dt_time(9, 15)
MARKET_END_TIME = dt_time(15, 30)
SCAN_INTERVAL_MINUTES = 10

# Title and instructions
st.title("9-21 EMA Crossover Scanner")
st.write("Scan Nifty 500 stocks for 1-hour EMA 9/21 crossovers. Click 'Run Scan' during market hours (9:15 AM - 3:30 PM IST).")

# Read stock symbols
symbols = read_stock_symbols()
if not symbols:
    st.error("No stock symbols found. Check nifty500.txt.")
else:
    st.write(f"Monitoring {len(symbols)} stocks.")

# Run button
if st.button("Run Scan"):
    now = pd.Timestamp.now(tz=TIMEZONE)
    if now.weekday() < 5 and MARKET_START_TIME <= now.time() <= MARKET_END_TIME:
        st.session_state.last_run = now
        st.write(f"Scanning at {now.strftime('%H:%M:%S IST')}...")
        scan_for_crossovers(symbols)
        st.success("Scan completed. Check Telegram for alerts.")
    else:
        st.warning(f"Market closed. Scans only run between 9:15 AM and 3:30 PM IST. Current time: {now.strftime('%H:%M:%S IST')}")

# Display last run time
if st.session_state.last_run:
    st.write(f"Last scan run at: {st.session_state.last_run.strftime('%H:%M:%S IST')}")

# Optional: Auto-refresh (simulated every 10 minutes, but limited by Streamlit's rerun)
if st.session_state.last_run and (pd.Timestamp.now(tz=TIMEZONE) - st.session_state.last_run).total_seconds() >= SCAN_INTERVAL_MINUTES * 60:
    st.experimental_rerun()  # Triggers a rerun if 10 minutes passed

# Startup message
if st.session_state.last_run is None:
    send_telegram_alert_sync("🔄 1-Hour EMA Scanner Started on Streamlit - Monitoring 500 stocks for 9/21 crossovers")
