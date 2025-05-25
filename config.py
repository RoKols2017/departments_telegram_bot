# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# ====== Базовые настройки ======
BOT_TOKEN = os.getenv('BOT_TOKEN')

# ====== ID суперадмина (заполни реальным ID) ======
SUPERADMIN_ID = int(os.getenv('SUPERADMIN_ID', 0))

# ====== Настройки БД ======
# Для разработки
DB_TYPE = os.getenv('DB_TYPE', 'sqlite')
DB_NAME = os.getenv('DB_NAME', 'database')
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = int(os.getenv('DB_PORT', 5432))

# Construct database URL
if DB_TYPE == 'postgresql':
    DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
else:
    DATABASE_URL = f"sqlite:///{Path('data')}/{DB_NAME}.db"

# ====== Прочее ======
BIRTHDAY_REMINDER_DAYS_BEFORE = 10   # За сколько дней до ДР напоминать админам
FUND_REMINDER_DAYS_BEFORE = 3        # За сколько дней до дедлайна сборов напоминать казначею

# Logging Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_DB_PATH = os.getenv('LOG_DB_PATH', 'data/logs.db')

# Rate Limiting
RATE_LIMIT = int(os.getenv('RATE_LIMIT', 5))
RATE_LIMIT_DURATION = int(os.getenv('RATE_LIMIT_DURATION', 60))

# Notification Settings
REMINDER_HOUR = int(os.getenv('REMINDER_HOUR', 10))
BIRTHDAY_REMINDER_DAYS = int(os.getenv('BIRTHDAY_REMINDER_DAYS', 3))
FUND_REMINDER_DAYS = int(os.getenv('FUND_REMINDER_DAYS', 2))

# Security
ALLOWED_CHAT_TYPES = os.getenv('ALLOWED_CHAT_TYPES', 'private,group').split(',')
MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', 4096))
ALLOWED_FILE_TYPES = os.getenv('ALLOWED_FILE_TYPES', 'image/jpeg,image/png,application/pdf').split(',')

# Roles Configuration
ROLES = {
    'user': 1,
    'treasurer': 2,
    'admin': 3,
    'superadmin': 4
}

# Default values
DEFAULT_FUND_DURATION_DAYS = 14
DEFAULT_BIRTHDAY_FUND_AMOUNT = 1000
DEFAULT_EVENT_FUND_AMOUNT = 500
