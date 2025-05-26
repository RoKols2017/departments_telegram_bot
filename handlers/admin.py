# handlers/admin.py
from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import SessionLocal
from models import User, Staff
from keyboards import get_menu_by_role
from utils import is_admin
from utils import parse_date
from utils.decorators import with_db_session

router = Router()

# ---------- FSM ----------

class AddStaff(StatesGroup):
    waiting_for_staff_data = State()

class RemoveStaff(StatesGroup):
    waiting_for_personnel_number = State()

# ---------- Добавить сотрудника ----------

@router.message(Command("add_staff"))
@with_db_session
async def add_staff(message: types.Message, session, state: FSMContext):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user or not is_admin(user.role):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer(
        "Введите данные сотрудника в формате:\n\n"
        "`Табельный номер;Имя;Отчество;ДД.ММ.ГГГГ`\n\n"
        "Пример: `12345;Иван;Иванович;15.06.1990`",
        parse_mode="Markdown"
    )
    await state.set_state(AddStaff.waiting_for_staff_data)

@router.message(AddStaff.waiting_for_staff_data)
@with_db_session
async def process_add_staff(message: types.Message, session, state: FSMContext):
    try:
        personnel_number, first_name, patronymic, birthday_str = map(str.strip, message.text.split(";"))
        birthday_date = parse_date(birthday_str)
        if not birthday_date:
            await message.answer("❌ Неверный формат даты! Используйте ДД.ММ.ГГГГ")
            return
    except Exception:
        await message.answer("❌ Неверный формат! Используйте: `Табельный;Имя;Отчество;ДД.ММ.ГГГГ`",
                             parse_mode="Markdown")
        return
    if session.query(Staff).filter_by(personnel_number=personnel_number).first():
        await message.answer("❌ Сотрудник с таким табельным номером уже существует.")
        await state.clear()
        return
    new_staff = Staff(
        personnel_number=personnel_number,
        first_name=first_name,
        patronymic=patronymic,
        birthday=birthday_date
    )
    session.add(new_staff)
    session.commit()
    await message.answer(f"✅ Сотрудник {first_name} {patronymic} добавлен.")
    await state.clear()

# ---------- Удалить сотрудника ----------

@router.message(Command("remove_staff"))
@with_db_session
async def remove_staff(message: types.Message, session, state: FSMContext):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user or not is_admin(user.role):
        await message.answer("⛔ Нет доступа.")
        return
    await message.answer("Введите табельный номер сотрудника для удаления:")
    await state.set_state(RemoveStaff.waiting_for_personnel_number)

@router.message(RemoveStaff.waiting_for_personnel_number)
@with_db_session
async def process_remove_staff(message: types.Message, session, state: FSMContext):
    personnel_number = message.text.strip()
    staff = session.query(Staff).filter_by(personnel_number=personnel_number).first()
    if not staff:
        await message.answer("❌ Сотрудник с таким табельным номером не найден.")
        await state.clear()
        return
    session.delete(staff)
    session.commit()
    await message.answer(f"✅ Сотрудник с табельным номером {personnel_number} удалён.")
    await state.clear()
