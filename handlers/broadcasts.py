# handlers/broadcasts.py

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from database import SessionLocal
from models import User, Fund, Donation, Staff
from utils import ensure_registered
from datetime import datetime

router = Router()

# ---------- FSM ----------

class FundReminder(StatesGroup):
    waiting_for_text = State()

# ---------- Команда рассылки для казначея ----------

@router.message(Command("remind_fund"))
@ensure_registered()
async def remind_fund_entry(message: types.Message, state: FSMContext, user: User):
    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer("❌ Укажите команду в формате `/remind_fund <id_сбора>`", parse_mode="Markdown")
        return

    fund_id = int(args[1])
    session = SessionLocal()
    try:
        fund = session.query(Fund).filter_by(id=fund_id).first()
        if not fund:
            await message.answer("❌ Сбор не найден.")
            return

        if fund.is_closed:
            await message.answer("⚠️ Сбор уже закрыт.")
            return

        if fund.treasurer_id != user.id:
            await message.answer("⛔ Вы не казначей этого сбора.")
            return

        await state.update_data(fund_id=fund_id)
        await message.answer("Введите текст напоминания:")
        await state.set_state(FundReminder.waiting_for_text)
    finally:
        session.close()

@router.message(FundReminder.waiting_for_text)
async def process_fund_reminder(message: types.Message, state: FSMContext):
    text = message.text.strip()
    session = SessionLocal()
    try:
        data = await state.get_data()
        fund_id = data.get("fund_id")

        fund = session.query(Fund).filter_by(id=fund_id).first()
        if not fund:
            await message.answer("❌ Сбор не найден.")
            await state.clear()
            return

        # список всех участников
        users = session.query(User).all()

        # список сдавших
        paid_user_ids = {don.user_id for don in session.query(Donation).filter_by(fund_id=fund_id).all()}

        # исключаем именинника, если сбор на ДР
        exclude_ids = set(paid_user_ids)
        if fund.type == "birthday" and fund.staff_id:
            birthday_user = session.query(User).filter_by(staff_id=fund.staff_id).first()
            if birthday_user:
                exclude_ids.add(birthday_user.id)

        count = 0
        for u in users:
            if u.id not in exclude_ids:
                try:
                    await message.bot.send_message(u.telegram_id, f"💸 Напоминание от казначея:\n\n{text}")
                    count += 1
                except Exception:
                    continue

        await message.answer(f"✅ Рассылка выполнена. Отправлено: {count} сообщений.")
        await state.clear()
    finally:
        session.close()
