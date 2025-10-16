# alerts.py
import os
import telegram
import asyncio
import streamlit as st  # Add this import for st.secrets

def get_telegram_config():
    """Reads Telegram configuration from Streamlit secrets (or fallback to env for local testing)"""
    # Try Streamlit secrets first (for cloud deployment)
    if hasattr(st, 'secrets'):
        bot_token = st.secrets.get('TELEGRAM_BOT_TOKEN')
        chat_id = st.secrets.get('TELEGRAM_CHAT_ID')
    else:
        # Fallback to .env for local runs (using dotenv)
        from dotenv import load_dotenv
        load_dotenv()
        bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Error: Telegram configuration not found")
        return None, None
    
    return bot_token, chat_id

async def send_telegram_alert(message):
    """Sends a message to Telegram using credentials from secrets/env"""
    bot_token, chat_id = get_telegram_config()
    
    if not bot_token or not chat_id:
        return
    
    try:
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"✓ Telegram alert sent: {message[:50]}...")
    except telegram.error.TelegramError as e:
        print(f"✗ Telegram error: {e}")
    except Exception as e:
        print(f"✗ Error sending Telegram alert: {e}")

# Synchronous wrapper for easier use
def send_telegram_alert_sync(message):
    """Synchronous wrapper for sending Telegram alerts"""
    asyncio.run(send_telegram_alert(message))
