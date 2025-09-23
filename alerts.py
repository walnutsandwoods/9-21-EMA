import configparser
import telegram
import asyncio
import os

# --- Use Absolute Path for Config File ---
# This makes the script runnable from any directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'config.ini')

def read_config():
    """Reads Telegram configuration from config.ini"""
    config = configparser.ConfigParser()

    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file not found at path: {CONFIG_FILE}")
        print("Please ensure 'config.ini' exists in the same directory as the script.")
        return None, None

    config.read(CONFIG_FILE)

    if 'telegram' in config and 'bot_token' in config['telegram'] and 'chat_id' in config['telegram']:
        bot_token = config['telegram']['bot_token']
        chat_id = config['telegram']['chat_id']

        if 'YOUR_BOT_TOKEN_HERE' in bot_token or 'YOUR_CHAT_ID_HERE' in chat_id:
            print("Error: Please replace the placeholder values in your config.ini file with your actual credentials.")
            return None, None

        return bot_token, chat_id
    else:
        print("Error: A [telegram] section with 'bot_token' and 'chat_id' was not found in config.ini.")
        return None, None

async def send_telegram_alert(bot_token, chat_id, message):
    """Sends a message to a Telegram user or group."""
    try:
        bot = telegram.Bot(token=bot_token)
        await bot.send_message(chat_id=chat_id, text=message)
        print(f"Telegram alert sent successfully.")
    except Exception as e:
        print(f"Error sending Telegram alert: {e}")
