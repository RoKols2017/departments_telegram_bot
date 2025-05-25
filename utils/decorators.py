# utils/decorators.py

from functools import wraps
from aiogram import types
from database import SessionLocal
from models import User, Log
from datetime import datetime

def role_required(roles: list[str]):
    """
    Проверка ролей пользователя
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            session = SessionLocal()
            try:
                user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
                if not user:
                    await message.answer("❌ Вы не зарегистрированы.")
                    return

                if user.role not in roles:
                    await message.answer("⛔ Нет доступа к этой команде.")
                    return

                return await handler(message, user, *args, **kwargs)
            finally:
                session.close()
        return wrapper
    return decorator


def ensure_registered():
    """
    Проверка регистрации
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            session = SessionLocal()
            try:
                user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
                if not user:
                    await message.answer("❌ Вы не зарегистрированы. Введите /start для регистрации.")
                    return
                return await handler(message, user, *args, **kwargs)
            finally:
                session.close()
        return wrapper
    return decorator


def log_action(action_name: str):
    """
    Логирование действий пользователя
    """
    def decorator(handler):
        @wraps(handler)
        async def wrapper(message: types.Message, *args, **kwargs):
            session = SessionLocal()
            try:
                session.add(Log(user_id=message.from_user.id, action=action_name, timestamp=datetime.utcnow()))
                session.commit()
            finally:
                session.close()
            return await handler(message, *args, **kwargs)
        return wrapper
    return decorator
