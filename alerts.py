import configparser
import telegram
import asyncio
import os

CONFIG_FILE = 'config.ini'

def read_config():
    """Reads Telegram configuration from config.ini"""

    # --- New Debugging Logic ---
    current_directory = os.getcwd()
    print(f"\n--- Debugging File Path ---")
    print(f"I am running in this directory: {current_directory}")
    print(f"I am looking for a file named '{CONFIG_FILE}' in this directory.")

    try:
        files_in_dir = os.listdir(current_directory)
        print("Files and folders I can see here:")
        for name in files_in_dir:
            print(f"- {name}")
    except Exception as e:
        print(f"Could not list files in the directory. Error: {e}")
    print(f"---------------------------\n")
    # --- End Debugging Logic ---

    config = configparser.ConfigParser()
    # Check if the file exists and read it
    if not config.read(CONFIG_FILE):
        print(f"Error: Configuration file '{CONFIG_FILE}' not found or is empty.")
        print("Please make sure you have created this file and added your credentials.")
        return None, None

    if 'telegram' in config and 'bot_token' in config['telegram'] and 'chat_id' in config['telegram']:
        # Add a check for placeholder values
        if 'YOUR_BOT_TOKEN_HERE' in config['telegram']['bot_token'] or 'YOUR_CHAT_ID_HERE' in config['telegram']['chat_id']:
            print("Error: Please replace the placeholder values in your config.ini file with your actual credentials.")
            return None, None
        return config['telegram']['bot_token'], config['telegram']['chat_id']
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
