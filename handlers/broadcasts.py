# handlers/broadcasts.py

from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from models import User, Donation
from utils.decorators import with_db_session_async
from services.fund_service import FundService
from sqlalchemy import select

router = Router()

# ---------- FSM ----------


class FundReminder(StatesGroup):
    waiting_for_text = State()


# ---------- Команда рассылки для казначея ----------


@router.message(Command("remind_fund"))
@with_db_session_async
async def remind_fund_entry(message: types.Message, session, state: FSMContext):
    args = message.text.strip().split()
    if len(args) != 2 or not args[1].isdigit():
        await message.answer(
            "❌ Укажите команду в формате `/remind_fund <id_сбора>`",
            parse_mode="Markdown",
        )
        return
    fund_id = int(args[1])
    fund_service = FundService(session)
    fund = await fund_service.get_fund(fund_id)
    if not fund:
        await message.answer("❌ Сбор не найден.")
        return
    if hasattr(fund, "is_closed") and fund.is_closed:
        await message.answer("⚠️ Сбор уже закрыт.")
        return
    if fund.treasurer_id != message.from_user.id:
        await message.answer("⛔ Вы не казначей этого сбора.")
        return
    await state.update_data(fund_id=fund_id)
    await message.answer("Введите текст напоминания:")
    await state.set_state(FundReminder.waiting_for_text)


@router.message(FundReminder.waiting_for_text)
@with_db_session_async
async def process_fund_reminder(message: types.Message, session, state: FSMContext):
    text = message.text.strip()
    data = await state.get_data()
    fund_id = data.get("fund_id")
    fund_service = FundService(session)
    fund = await fund_service.get_fund(fund_id)
    if not fund:
        await message.answer("❌ Сбор не найден.")
        await state.clear()
        return
    result = await session.execute(select(User))
    users = result.scalars().all()
    paid_result = await session.execute(
        select(Donation.user_id).where(Donation.fund_id == fund_id)
    )
    paid_user_ids = {user_id for (user_id,) in paid_result.all()}
    exclude_ids = set(paid_user_ids)
    if getattr(fund, "type", None) == "birthday" and getattr(fund, "staff_id", None):
        birthday_user_result = await session.execute(
            select(User).where(User.staff_id == fund.staff_id)
        )
        birthday_user = birthday_user_result.scalar_one_or_none()
        if birthday_user:
            exclude_ids.add(birthday_user.id)
    count = 0
    for u in users:
        if u.id not in exclude_ids:
            try:
                await message.bot.send_message(
                    u.telegram_id, f"💸 Напоминание от казначея:\n\n{text}"
                )
                count += 1
            except Exception:
                continue
    await message.answer(f"✅ Рассылка выполнена. Отправлено: {count} сообщений.")
    await state.clear()
