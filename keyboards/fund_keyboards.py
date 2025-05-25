from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def treasurer_fund_menu(fund_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="➕ Добавить сдачу", callback_data=f"add_donation:{fund_id}")],
            [InlineKeyboardButton(text="🔄 Напомнить должникам", callback_data=f"remind_unpaid:{fund_id}")],
            [InlineKeyboardButton(text="📊 Статус сбора", callback_data=f"fund_status:{fund_id}")],
            [InlineKeyboardButton(text="✅ Закрыть сбор", callback_data=f"close_fund:{fund_id}")]
        ]
    )

def back_button():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="back")]
        ]
    )
