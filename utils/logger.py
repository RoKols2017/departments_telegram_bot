import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path

def setup_logger(name: str, log_file: str, level=logging.INFO):
    """Настройка логгера с ротацией файлов"""
    
    # Создаем директорию для логов, если её нет
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Форматирование логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка файлового хендлера с ротацией
    file_handler = RotatingFileHandler(
        os.path.join(log_dir, log_file),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    
    # Настройка консольного хендлера
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Настройка логгера
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Создаем основные логгеры
bot_logger = setup_logger('bot', 'bot.log')
db_logger = setup_logger('database', 'database.log')
security_logger = setup_logger('security', 'security.log')
scheduler_logger = setup_logger('scheduler', 'scheduler.log')

def log_error(logger: logging.Logger, error: Exception, context: str = None):
    """Логирование ошибок с контекстом"""
    error_message = f"Error: {str(error)}"
    if context:
        error_message = f"Context: {context} - {error_message}"
    logger.error(error_message, exc_info=True)

def log_security_event(event_type: str, user_id: int, details: str):
    """Логирование событий безопасности"""
    security_logger.warning(
        f"Security event: {event_type} - User: {user_id} - Details: {details}"
    )
