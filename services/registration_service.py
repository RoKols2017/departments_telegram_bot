# services/registration_service.py
from sqlalchemy import select
from models import User

"""
Сервис регистрации: проверка регистрации пользователя по Telegram ID.
"""


async def is_registered(telegram_id: int, session) -> bool:
    """
    Проверяет, зарегистрирован ли пользователь с данным Telegram ID.
    Возвращает True, если пользователь найден в БД, иначе False.
    """
    result = await session.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none() is not None
