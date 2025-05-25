# keyboards/user_keyboards.py
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def user_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Мои данные")],
            [KeyboardButton(text="🎉 Именинники")],
            [KeyboardButton(text="💰 Активные сборы")]
        ],
        resize_keyboard=True
    )
