# services/registration_service.py
from database import SessionLocal
from models import User, Staff

"""
Сервис регистрации: проверка регистрации пользователя по Telegram ID.
"""

def is_registered(telegram_id: int, session) -> bool:
    """
    Проверяет, зарегистрирован ли пользователь с данным Telegram ID.
    Возвращает True, если пользователь найден в БД, иначе False.
    """
    return session.query(User).filter_by(telegram_id=telegram_id).first() is not None
