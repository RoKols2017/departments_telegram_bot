from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def admin_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📄 Мои данные"), KeyboardButton(text="🎉 Именинники")],
            [KeyboardButton(text="💰 Активные сборы"), KeyboardButton(text="➕ Добавить сотрудника")],
            [KeyboardButton(text="➖ Удалить сотрудника"), KeyboardButton(text="🎂 Создать сбор (ДР)")],
            [KeyboardButton(text="🎊 Создать сбор (Событие)"), KeyboardButton(text="💼 Назначить казначея")],
            [KeyboardButton(text="📢 Рассылка"), KeyboardButton(text="🚨 Повысить/Понизить/Удалить")]
        ],
        resize_keyboard=True
    )
