from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from database import SessionLocal
from models import User, Fund, Staff, FundType
from utils import is_admin
from datetime import datetime
from utils.decorators import with_db_session

router = Router()

# ---------- FSM ----------

class CreateBirthdayFund(StatesGroup):
    waiting_for_staff_id = State()
    waiting_for_deadline = State()

class CreateEventFund(StatesGroup):
    waiting_for_event_name = State()
    waiting_for_deadline = State()

# ---------- Создание сбора на ДР ----------

@router.message(Command("create_birthday_fund"))
@with_db_session
async def create_birthday_fund(message: types.Message, session, state: FSMContext):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user or not is_admin(user.role):
        await message.answer("Нет доступа.")
        return
    await message.answer("Введите табельный номер именинника для создания сбора:")
    await state.set_state(CreateBirthdayFund.waiting_for_staff_id)

@router.message(CreateBirthdayFund.waiting_for_staff_id)
@with_db_session
async def process_birthday_fund_staff(message: types.Message, session, state: FSMContext):
    staff_id = message.text.strip()
    staff = session.query(Staff).filter_by(personnel_number=staff_id).first()
    if not staff:
        await message.answer("❌ Сотрудник не найден.")
        return
    await state.update_data(staff_id=staff.id)
    await message.answer("Введите дату дедлайна сбора в формате ДД.ММ.ГГГГ:")
    await state.set_state(CreateBirthdayFund.waiting_for_deadline)

@router.message(CreateBirthdayFund.waiting_for_deadline)
@with_db_session
async def process_birthday_fund_deadline(message: types.Message, session, state: FSMContext):
    deadline_str = message.text.strip()
    try:
        day, month, year = map(int, deadline_str.split("."))
        deadline = datetime(year, month, day).date()
    except Exception:
        await message.answer("❌ Неверный формат даты.")
        return
    data = await state.get_data()
    new_fund = Fund(
        type=FundType.birthday,
        deadline=deadline,
        staff_id=data["staff_id"]
    )
    session.add(new_fund)
    session.commit()
    await message.answer("✅ Сбор на ДР успешно создан.")
    await state.clear()

# ---------- Создание сбора на Событие ----------

@router.message(Command("create_event_fund"))
@with_db_session
async def create_event_fund(message: types.Message, session, state: FSMContext):
    user = session.query(User).filter_by(telegram_id=message.from_user.id).first()
    if not user or not is_admin(user.role):
        await message.answer("Нет доступа.")
        return
    await message.answer("Введите название события:")
    await state.set_state(CreateEventFund.waiting_for_event_name)

@router.message(CreateEventFund.waiting_for_event_name)
async def process_event_name(message: types.Message, state: FSMContext):
    await state.update_data(event_name=message.text.strip())
    await message.answer("Введите дату дедлайна сбора в формате ДД.ММ.ГГГГ:")
    await state.set_state(CreateEventFund.waiting_for_deadline)

@router.message(CreateEventFund.waiting_for_deadline)
@with_db_session
async def process_event_deadline(message: types.Message, session, state: FSMContext):
    deadline_str = message.text.strip()
    try:
        day, month, year = map(int, deadline_str.split("."))
        deadline = datetime(year, month, day).date()
    except Exception:
        await message.answer("❌ Неверный формат даты.")
        return
    data = await state.get_data()
    new_fund = Fund(
        type=FundType.event,
        deadline=deadline,
        event_name=data["event_name"]
    )
    session.add(new_fund)
    session.commit()
    await message.answer("✅ Сбор на событие успешно создан.")
    await state.clear()
