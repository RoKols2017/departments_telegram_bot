# handlers/admin.py
from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from models import Staff
from utils import is_admin
from utils import parse_date
from utils.decorators import with_db_session_async
from services.user_service import UserService
from sqlalchemy import select

router = Router()

# ---------- FSM ----------


class AddStaff(StatesGroup):
    waiting_for_staff_data = State()


class RemoveStaff(StatesGroup):
    waiting_for_personnel_number = State()


# ---------- Добавить сотрудника ----------


@router.message(Command("add_staff"))
@with_db_session_async
async def add_staff(message: types.Message, session, state: FSMContext):
    user_service = UserService(session)
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if not user or not is_admin(user.role):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer(
        "Введите данные сотрудника в формате:\n\n"
        "`Табельный номер;Имя;Отчество;ДД.ММ.ГГГГ`\n\n"
        "Пример: `12345;Иван;Иванович;15.06.1990`",
        parse_mode="Markdown",
    )
    await state.set_state(AddStaff.waiting_for_staff_data)


@router.message(AddStaff.waiting_for_staff_data)
@with_db_session_async
async def process_add_staff(message: types.Message, session, state: FSMContext):
    try:
        personnel_number, first_name, patronymic, birthday_str = map(
            str.strip, message.text.split(";")
        )
        birthday_date = parse_date(birthday_str)
        if not birthday_date:
            await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return
    except Exception:
        await message.answer(
            "❌ Неверный формат! Используйте: `Табельный;Имя;Отчество;ДД.ММ.ГГГГ`",
            parse_mode="Markdown",
        )
        return
    result = await session.execute(
        select(Staff).where(Staff.personnel_number == personnel_number)
    )
    staff = result.scalar_one_or_none()
    if staff:
        await message.answer("❌ Сотрудник с таким табельным номером уже существует.")
        await state.clear()
        return
    new_staff = Staff(
        personnel_number=personnel_number,
        first_name=first_name,
        patronymic=patronymic,
        birthday=birthday_date,
    )
    session.add(new_staff)
    await session.commit()
    await message.answer(f"✅ Сотрудник {first_name} {patronymic} добавлен.")
    await state.clear()


# ---------- Удалить сотрудника ----------


@router.message(Command("remove_staff"))
@with_db_session_async
async def remove_staff(message: types.Message, session, state: FSMContext):
    user_service = UserService(session)
    user = await user_service.get_user_by_telegram_id(message.from_user.id)
    if not user or not is_admin(user.role):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer("Введите табельный номер сотрудника для удаления:")
    await state.set_state(RemoveStaff.waiting_for_personnel_number)


@router.message(RemoveStaff.waiting_for_personnel_number)
@with_db_session_async
async def process_remove_staff(message: types.Message, session, state: FSMContext):
    personnel_number = message.text.strip()
    result = await session.execute(
        select(Staff).where(Staff.personnel_number == personnel_number)
    )
    staff = result.scalar_one_or_none()
    if not staff:
        await message.answer("❌ Сотрудник с таким табельным номером не найден.")
        await state.clear()
        return
    await session.delete(staff)
    await session.commit()
    await message.answer(f"✅ Сотрудник с табельным номером {personnel_number} удалён.")
    await state.clear()
