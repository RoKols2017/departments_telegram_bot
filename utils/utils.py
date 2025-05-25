from aiogram.types import BotCommand
from typing import List, Dict, Any
from datetime import datetime, timedelta
import re

def setup_bot_commands() -> List[BotCommand]:
    """Настройка команд бота"""
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="menu", description="Главное меню"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="mydata", description="Мои данные"),
        BotCommand(command="birthdays", description="Список именинников"),
        BotCommand(command="active_funds", description="Активные сборы"),
        BotCommand(command="my_donations", description="Мои взносы"),
        BotCommand(command="notifications", description="Мои уведомления")
    ]
    return commands

def setup_treasurer_commands() -> List[BotCommand]:
    """Команды для казначея"""
    commands = [
        BotCommand(command="add_donation", description="Добавить взнос"),
        BotCommand(command="fund_status", description="Статус сбора"),
        BotCommand(command="remind_unpaid", description="Напомнить о взносе"),
        BotCommand(command="close_fund", description="Закрыть сбор")
    ]
    return commands

def setup_admin_commands() -> List[BotCommand]:
    """Команды для администратора"""
    commands = [
        BotCommand(command="add_staff", description="Добавить сотрудника"),
        BotCommand(command="remove_staff", description="Удалить сотрудника"),
        BotCommand(command="create_birthday_fund", description="Создать сбор на ДР"),
        BotCommand(command="create_event_fund", description="Создать сбор на событие"),
        BotCommand(command="assign_treasurer", description="Назначить казначея"),
        BotCommand(command="broadcast", description="Создать рассылку"),
        BotCommand(command="birthday_broadcast", description="Рассылка без именинников"),
        BotCommand(command="announcement", description="Объявление")
    ]
    return commands

def setup_superadmin_commands() -> List[BotCommand]:
    """Команды для суперадминистратора"""
    commands = [
        BotCommand(command="promote_user", description="Назначить админом"),
        BotCommand(command="demote_admin", description="Снять с админов"),
        BotCommand(command="remove_user", description="Удалить пользователя")
    ]
    return commands

def validate_employee_id(employee_id: str) -> bool:
    """Проверка корректности табельного номера"""
    pattern = r'^\d{6}$'  # Шесть цифр
    return bool(re.match(pattern, employee_id))

def format_money(amount: float) -> str:
    """Форматирование денежной суммы"""
    return f"{amount:,.2f}₽".replace(",", " ")

def format_date(date: datetime) -> str:
    """Форматирование даты"""
    return date.strftime("%d.%m.%Y")

def calculate_days_until(target_date: datetime) -> int:
    """Расчет количества дней до даты"""
    return (target_date - datetime.now()).days

def format_fund_status(fund_data: Dict[str, Any]) -> str:
    """Форматирование статуса сбора"""
    status = f"📊 Сбор: {fund_data['title']}\n"
    status += f"💰 Цель: {format_money(fund_data['target_amount'])}\n"
    status += f"💵 Собрано: {format_money(fund_data['current_amount'])}\n"
    status += f"⏳ Осталось собрать: {format_money(fund_data['remaining_amount'])}\n"
    status += f"👥 Внесли взнос: {fund_data['donors_count']} человек\n"
    status += f"📅 Дней до закрытия: {fund_data['days_left']}\n"
    status += f"Статус: {'🟢 Активен' if fund_data['is_active'] else '🔴 Закрыт'}"
    return status

def format_notification(title: str, message: str, created_at: datetime) -> str:
    """Форматирование уведомления"""
    return f"📬 {title}\n\n{message}\n\nПолучено: {format_date(created_at)}"

def is_valid_amount(amount: str) -> bool:
    """Проверка корректности суммы"""
    try:
        amount = float(amount.replace(" ", "").replace(",", "."))
        return amount > 0
    except ValueError:
        return False

def parse_amount(amount: str) -> float:
    """Преобразование строки в денежную сумму"""
    return float(amount.replace(" ", "").replace(",", "."))

def get_role_emoji(role: str) -> str:
    """Получение эмодзи для роли"""
    role_emojis = {
        "user": "👤",
        "treasurer": "💰",
        "admin": "🛠",
        "superadmin": "👑"
    }
    return role_emojis.get(role, "❓") 