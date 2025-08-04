import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot settings
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_USER_ID = os.getenv('TELEGRAM_USER_ID')

# Website monitoring settings
TARGET_URL = os.getenv('TARGET_URL', '')
SEARCH_NAMES = os.getenv('SEARCH_NAMES', '').split(',')  # Comma-separated names
CHECK_INTERVAL_MINUTES = int(os.getenv('CHECK_INTERVAL_MINUTES', '10'))

# Logging
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO') 