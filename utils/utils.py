"""
Вспомогательные функции для форматирования, валидации и генерации команд Telegram-бота.
"""

from aiogram.types import BotCommand
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re


def setup_bot_commands() -> List[BotCommand]:
    """
    Возвращает список базовых команд для пользователя.

    Returns:
        List[BotCommand]: Список команд.
    """
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="mydata", description="Мои данные"),
        BotCommand(command="birthdays", description="Список именинников"),
        BotCommand(command="active_funds", description="Активные сборы"),
        BotCommand(command="my_donations", description="Мои взносы"),
        BotCommand(command="notifications", description="Мои уведомления"),
    ]
    return commands


def setup_treasurer_commands() -> List[BotCommand]:
    """
    Возвращает список команд для казначея.

    Returns:
        List[BotCommand]: Список команд.
    """
    commands = [
        BotCommand(command="add_donation", description="Добавить взнос"),
        BotCommand(command="fund_status", description="Статус сбора"),
        BotCommand(command="remind_unpaid", description="Напомнить о взносе"),
        BotCommand(command="close_fund", description="Закрыть сбор"),
    ]
    return commands


def setup_admin_commands() -> List[BotCommand]:
    """
    Возвращает список команд для администратора.

    Returns:
        List[BotCommand]: Список команд.
    """
    commands = [
        BotCommand(command="add_staff", description="Добавить сотрудника"),
        BotCommand(command="remove_staff", description="Удалить сотрудника"),
        BotCommand(command="create_birthday_fund", description="Создать сбор на ДР"),
        BotCommand(command="create_event_fund", description="Создать сбор на событие"),
        BotCommand(command="assign_treasurer", description="Назначить казначея"),
        BotCommand(command="broadcast", description="Создать рассылку"),
        BotCommand(
            command="birthday_broadcast", description="Рассылка без именинников"
        ),
        BotCommand(command="announcement", description="Объявление"),
    ]
    return commands


def setup_superadmin_commands() -> List[BotCommand]:
    """
    Возвращает список команд для суперадминистратора.

    Returns:
        List[BotCommand]: Список команд.
    """
    commands = [
        BotCommand(command="promote_user", description="Назначить админом"),
        BotCommand(command="demote_admin", description="Снять с админов"),
        BotCommand(command="remove_user", description="Удалить пользователя"),
    ]
    return commands


def validate_employee_id(employee_id: str) -> bool:
    """
    Проверяет корректность табельного номера (6 цифр).

    Args:
        employee_id (str): Табельный номер.

    Returns:
        bool: True, если номер корректен.
    """
    pattern = r"^\d{6}$"  # Шесть цифр
    return bool(re.match(pattern, employee_id))


def format_money(amount: float) -> str:
    """
    Форматирует денежную сумму с разделителем тысяч и знаком рубля.

    Args:
        amount (float): Сумма.

    Returns:
        str: Отформатированная сумма.
    """
    return f"{amount:,.2f}₽".replace(",", " ")


def format_date(date: datetime) -> str:
    """
    Форматирует дату в строку вида 'ДД.ММ.ГГГГ'.

    Args:
        date (datetime): Дата.

    Returns:
        str: Отформатированная дата.
    """
    return date.strftime("%d.%m.%Y")


def calculate_days_until(target_date: datetime) -> int:
    """
    Возвращает количество дней до указанной даты.

    Args:
        target_date (datetime): Целевая дата.

    Returns:
        int: Количество дней.
    """
    return (target_date - datetime.now()).days


def format_fund_status(fund_data: Dict[str, Any]) -> str:
    """
    Форматирует статус сбора для отображения пользователю.

    Args:
        fund_data (Dict[str, Any]): Данные о сборе.

    Returns:
        str: Строка со статусом сбора.
    """
    status = f"📊 Сбор: {fund_data['title']}\n"
    status += f"💰 Цель: {format_money(fund_data['target_amount'])}\n"
    status += f"💵 Собрано: {format_money(fund_data['current_amount'])}\n"
    status += f"⏳ Осталось собрать: {format_money(fund_data['remaining_amount'])}\n"
    status += f"👥 Внесли взнос: {fund_data['donors_count']} человек\n"
    status += f"📅 Дней до закрытия: {fund_data['days_left']}\n"
    status += f"Статус: {'🟢 Активен' if fund_data['is_active'] else '🔴 Закрыт'}"
    return status


def format_notification(title: str, message: str, created_at: datetime) -> str:
    """
    Форматирует уведомление для пользователя.

    Args:
        title (str): Заголовок.
        message (str): Сообщение.
        created_at (datetime): Дата создания.

    Returns:
        str: Отформатированное уведомление.
    """
    return f"📬 {title}\n\n{message}\n\nПолучено: {format_date(created_at)}"


def is_valid_amount(amount: str) -> bool:
    """
    Проверяет корректность строки с суммой.

    Args:
        amount (str): Строка с суммой.

    Returns:
        bool: True, если сумма корректна.
    """
    try:
        amount = float(amount.replace(" ", "").replace(",", "."))
        return amount > 0
    except ValueError:
        return False


def parse_amount(amount: str) -> float:
    """
    Преобразует строку в число с плавающей точкой (сумму).

    Args:
        amount (str): Строка с суммой.

    Returns:
        float: Сумма.
    """
    return float(amount.replace(" ", "").replace(",", "."))


def get_role_emoji(role: str) -> str:
    """
    Возвращает эмодзи для роли пользователя.

    Args:
        role (str): Название роли.

    Returns:
        str: Эмодзи.
    """
    role_emojis = {"user": "👤", "treasurer": "💰", "admin": "🛠", "superadmin": "👑"}
    return role_emojis.get(role, "❓")
