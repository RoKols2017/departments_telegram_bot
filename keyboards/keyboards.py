from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from typing import List, Optional

def get_main_keyboard(roles: List[str]) -> ReplyKeyboardMarkup:
    """Главная клавиатура с учетом ролей пользователя"""
    buttons = [
        [KeyboardButton(text="📊 Активные сборы"), KeyboardButton(text="🎂 Именинники")],
        [KeyboardButton(text="💰 Мои взносы"), KeyboardButton(text="📬 Уведомления")]
    ]
    
    if "treasurer" in roles:
        buttons.append([KeyboardButton(text="💼 Управление сборами")])
    
    if "admin" in roles:
        buttons.append([KeyboardButton(text="👥 Управление сотрудниками")])
        buttons.append([KeyboardButton(text="📢 Рассылки")])
    
    if "superadmin" in roles:
        buttons.append([KeyboardButton(text="⚙️ Управление ролями")])
    
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_treasurer_keyboard(fund_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """Клавиатура казначея"""
    buttons = []
    
    if fund_id:
        buttons.extend([
            [InlineKeyboardButton(text="➕ Добавить взнос", callback_data=f"add_donation:{fund_id}")],
            [InlineKeyboardButton(text="📊 Статус сбора", callback_data=f"fund_status:{fund_id}")],
            [InlineKeyboardButton(text="🔔 Напомнить о взносе", callback_data=f"remind_unpaid:{fund_id}")],
            [InlineKeyboardButton(text="✅ Закрыть сбор", callback_data=f"close_fund:{fund_id}")]
        ])
    else:
        buttons.extend([
            [InlineKeyboardButton(text="📋 Мои сборы", callback_data="my_funds")],
            [InlineKeyboardButton(text="📊 Статистика", callback_data="treasurer_stats")]
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_admin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура администратора"""
    buttons = [
        [
            InlineKeyboardButton(text="➕ Добавить сотрудника", callback_data="add_staff"),
            InlineKeyboardButton(text="➖ Удалить сотрудника", callback_data="remove_staff")
        ],
        [
            InlineKeyboardButton(text="🎂 Создать сбор на ДР", callback_data="create_birthday_fund"),
            InlineKeyboardButton(text="🎉 Создать сбор на событие", callback_data="create_event_fund")
        ],
        [
            InlineKeyboardButton(text="💰 Назначить казначея", callback_data="assign_treasurer")
        ],
        [
            InlineKeyboardButton(text="📢 Общая рассылка", callback_data="broadcast"),
            InlineKeyboardButton(text="📣 Объявление", callback_data="announcement")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_superadmin_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура суперадминистратора"""
    buttons = [
        [
            InlineKeyboardButton(text="👑 Назначить админа", callback_data="promote_admin"),
            InlineKeyboardButton(text="👎 Снять админа", callback_data="demote_admin")
        ],
        [
            InlineKeyboardButton(text="❌ Удалить пользователя", callback_data="remove_user")
        ],
        [
            InlineKeyboardButton(text="📊 Статистика системы", callback_data="system_stats")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_fund_list_keyboard(funds: List[dict]) -> InlineKeyboardMarkup:
    """Клавиатура со списком сборов"""
    buttons = []
    for fund in funds:
        buttons.append([
            InlineKeyboardButton(
                text=f"{fund['title']} ({fund['current_amount']}/{fund['target_amount']}₽)",
                callback_data=f"fund:{fund['id']}"
            )
        ])
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_confirmation_keyboard(action: str, item_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения действия"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Да", callback_data=f"confirm_{action}:{item_id}"),
            InlineKeyboardButton(text="❌ Нет", callback_data=f"cancel_{action}:{item_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_notification_keyboard(notification_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для уведомления"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Прочитано", callback_data=f"read_notification:{notification_id}"),
            InlineKeyboardButton(text="🔔 Напомнить позже", callback_data=f"remind_later:{notification_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_broadcast_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа рассылки"""
    buttons = [
        [
            InlineKeyboardButton(text="👥 Всем", callback_data="broadcast_all"),
            InlineKeyboardButton(text="🎂 Кроме именинников", callback_data="broadcast_no_birthday")
        ],
        [
            InlineKeyboardButton(text="🏢 По отделу", callback_data="broadcast_department")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def get_back_keyboard(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Клавиатура с кнопкой "Назад\""""
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data)]]
    ) 