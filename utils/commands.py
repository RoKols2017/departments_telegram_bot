from aiogram import Bot
from aiogram.types import BotCommand, BotCommandScopeAllPrivateChats, BotCommandScopeChat

def get_default_commands():
    return [
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="mydata", description="Мои данные"),
        BotCommand(command="birthdays", description="Именинники"),
        BotCommand(command="active_funds", description="Активные сборы")
    ]

def get_admin_commands():
    return [
        BotCommand(command="menu", description="Открыть меню"),
        BotCommand(command="mydata", description="Мои данные"),
        BotCommand(command="birthdays", description="Именинники"),
        BotCommand(command="active_funds", description="Активные сборы"),
        BotCommand(command="add_staff", description="Добавить сотрудника"),
        BotCommand(command="remove_staff", description="Удалить сотрудника"),
        BotCommand(command="create_birthday_fund", description="Создать сбор (ДР)"),
        BotCommand(command="create_event_fund", description="Создать сбор (Событие)"),
        BotCommand(command="assign_treasurer", description="Назначить казначея"),
        BotCommand(command="broadcast", description="Рассылка всем"),
        BotCommand(command="birthday_broadcast", description="Рассылка без именинников"),
        BotCommand(command="announcement", description="Объявление")
    ]

async def set_commands_by_role(bot: Bot, telegram_id: int, role: str):
    if role in ["admin", "superadmin"]:
        commands = get_admin_commands()
    else:
        commands = get_default_commands()

    await bot.set_my_commands(commands, scope=BotCommandScopeChat(chat_id=telegram_id))
