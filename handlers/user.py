from aiogram import Router, F, types
from aiogram.filters import Command
from database import SessionLocal
from models import User
from utils import get_birthday_staff_ids
from keyboards import user_menu, get_menu_by_role

router = Router()

@router.message(Command("menu"))
@router.message(F.text == "📄 Мои данные")  # кнопка
async def show_menu(message: types.Message):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if user:
            await message.answer("Меню:", reply_markup=get_menu_by_role(user.role))
        else:
            await message.answer("Вы не зарегистрированы.")
    finally:
        session.close()

@router.message(Command("mydata"))
@router.message(F.text == "📄 Мои данные")
async def show_my_data(message: types.Message):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
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
    finally:
        session.close()
