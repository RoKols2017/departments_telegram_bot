from aiogram import Bot


async def remind_admins(bot: Bot, admin_ids: list[int], text: str):
    for admin_id in admin_ids:
        try:
            await bot.send_message(admin_id, text)
        except Exception as e:
            print(f"Ошибка при отправке уведомления админу {admin_id}: {e}")


async def remind_user(bot: Bot, user_id: int, text: str):
    try:
        await bot.send_message(user_id, text)
    except Exception as e:
        print(f"Ошибка при отправке уведомления пользователю {user_id}: {e}")
