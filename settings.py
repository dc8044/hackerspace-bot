import os
import re

# Enable this if you want to be able to use the debug command.
DEBUG = False

# Bot token provided by BotFather
TOKEN = os.environ.get('TELEGRAM_TOKEN')

PORT = int(os.environ.get('PORT', 8443))

APP_URL = os.environ.get('APP_URL')

ADMIN_CHAT_ID = int(os.environ.get('ADMIN_CHAT_ID'))

# Database info
DATABASE_URL = os.environ.get('DATABASE_URL')
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

LOCAL_BROKER = os.environ.get('REDIS_URL')
