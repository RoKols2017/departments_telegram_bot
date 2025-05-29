from aiogram import Router, types
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from models import Staff, User
from keyboards import get_menu_by_role
from utils import set_commands_by_role
from utils.decorators import with_db_session_async
from services.user_service import UserService
from sqlalchemy import select

router = Router()


class Registration(StatesGroup):
    waiting_for_personnel_number = State()


@router.message(Command("start"))
@with_db_session_async
async def cmd_start(message: types.Message, session, state: FSMContext):
    user_service = UserService(session)
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if user:
        await set_commands_by_role(message.bot, message.from_user.id, user.role)
        await message.answer(
            "Вы уже зарегистрированы.", reply_markup=get_menu_by_role(user.role)
        )
        return
    await message.answer("Введите табельный номер для регистрации:")
    await state.set_state(Registration.waiting_for_personnel_number)


@router.message(Registration.waiting_for_personnel_number)
@with_db_session_async
async def process_personnel_number(message: types.Message, session, state: FSMContext):
    personnel_number = message.text.strip()
    result = await session.execute(
        select(Staff).where(Staff.personnel_number == personnel_number)
    )
    staff = result.scalar_one_or_none()
    if not staff:
        await message.answer("Сотрудник с таким табельным номером не найден.")
        return
    user = User(telegram_id=message.from_user.id, staff_id=staff.id, role="user")
    session.add(user)
    await session.commit()
    await set_commands_by_role(message.bot, message.from_user.id, user.role)
    await message.answer(
        "✅ Регистрация успешна.", reply_markup=get_menu_by_role(user.role)
    )
    await state.clear()
