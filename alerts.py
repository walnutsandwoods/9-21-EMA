# alerts.py
import os
import telegram
import asyncio
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_telegram_config():
    """Reads Telegram configuration from .env file"""
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not bot_token or not chat_id:
        print("Error: Telegram configuration not found in .env file")
        print("Please make sure TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are set in your .env file")
        return None, None
    
    return bot_token, chat_id

async def send_telegram_alert(message):
    """Sends a message to Telegram using credentials from .env"""
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