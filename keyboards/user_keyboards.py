# keyboards/user_keyboards.py
"""
Генерация клавиатуры пользователя для Telegram-бота.
"""

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def user_menu() -> ReplyKeyboardMarkup:
    """
    Возвращает клавиатуру пользователя с основными действиями.

    Returns:
        ReplyKeyboardMarkup: Клавиатура пользователя.
    """
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Мои данные")],
            [KeyboardButton(text="🎉 Именинники")],
            [KeyboardButton(text="💰 Активные сборы")]
        ],
        resize_keyboard=True
    )
