"""
Генерация inline-клавиатур для управления сборами (фондом) в Telegram-боте.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def treasurer_fund_menu(fund_id: int) -> InlineKeyboardMarkup:
    """
    Возвращает inline-клавиатуру для казначея по управлению сбором.

    Args:
        fund_id (int): Идентификатор сбора.

    Returns:
        InlineKeyboardMarkup: Клавиатура казначея для сбора.
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить сдачу", callback_data=f"add_donation:{fund_id}")],
            [InlineKeyboardButton(text="🔄 Напомнить должникам", callback_data=f"remind_unpaid:{fund_id}")],
            [InlineKeyboardButton(text="📊 Статус сбора", callback_data=f"fund_status:{fund_id}")],
            [InlineKeyboardButton(text="✅ Закрыть сбор", callback_data=f"close_fund:{fund_id}")]
        ]
    )

def back_button() -> InlineKeyboardMarkup:
    """
    Возвращает inline-клавиатуру с кнопкой "Назад".

    Returns:
        InlineKeyboardMarkup: Клавиатура с кнопкой "Назад".
    """
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
    )
