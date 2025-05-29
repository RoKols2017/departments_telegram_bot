from aiogram import Router, types
from aiogram.filters import Command
from utils.decorators import with_db_session_async
from services.user_service import UserService
from keyboards import get_menu_by_role

router = Router()


@router.message(Command("menu"))
@router.message(types.Message.text == "📄 Мои данные")  # кнопка
@with_db_session_async
async def show_menu(message: types.Message, session):
    user_service = UserService(session)
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer("Меню:", reply_markup=get_menu_by_role(user.role))
    else:
        await message.answer("Вы не зарегистрированы.")


@router.message(Command("mydata"))
@router.message(types.Message.text == "📄 Мои данные")
@with_db_session_async
async def show_my_data(message: types.Message, session):
    user_service = UserService(session)
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer("Вы не зарегистрированы.")
        return
    staff = user.staff
    await message.answer(
        f"👤 Ваши данные:\n"
        f"Имя: {staff.first_name}\n"
        f"Отчество: {staff.patronymic}\n"
        f"Табельный номер: {staff.personnel_number}\n"
        f"Дата рождения: {staff.birthday.strftime('%d.%m.%Y')}\n"
        f"Роль: {user.role}"
    )
