from aiogram import Router, F, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from sqlalchemy.exc import SQLAlchemyError
from database import SessionLocal
from models import Staff, User, Log
from keyboards import get_menu_by_role
from utils import set_commands_by_role

router = Router()

class Registration(StatesGroup):
    waiting_for_personnel_number = State()

@router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    session = SessionLocal()
    try:
        user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
        if user:
            # динамическое popup меню
            await set_commands_by_role(message.bot, message.from_user.id, user.role)
            await message.answer("Вы уже зарегистрированы.", reply_markup=get_menu_by_role(user.role))
            return

        await message.answer("Введите табельный номер для регистрации:")
        await state.set_state(Registration.waiting_for_personnel_number)
    finally:
        session.close()

@router.message(Registration.waiting_for_personnel_number)
async def process_personnel_number(message: types.Message, state: FSMContext):
    personnel_number = message.text.strip()
    session = SessionLocal()
    try:
        staff = session.query(Staff).filter_by(personnel_number=personnel_number).first()
        if not staff:
            await message.answer("Сотрудник с таким табельным номером не найден.")
            return
        user = User(telegram_id=message.from_user.id, staff_id=staff.id, role="user")
        session.add(user)
        session.commit()

        # popup после регистрации
        await set_commands_by_role(message.bot, message.from_user.id, user.role)
        await message.answer("✅ Регистрация успешна.", reply_markup=get_menu_by_role(user.role))
        await state.clear()
    except SQLAlchemyError:
        await message.answer("Ошибка при регистрации.")
    finally:
        session.close()
