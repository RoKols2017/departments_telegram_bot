# keyboards/__init__.py
from .user_keyboards import user_menu
from .admin_keyboards import admin_menu
from .fund_keyboards import treasurer_fund_menu, back_button

__all__ = ["user_menu", "admin_menu", "treasurer_fund_menu", "back_button"]


def get_menu_by_role(role: str):
    """
    Возвращает клавиатуру в зависимости от роли пользователя
    """
    if role in ["admin", "superadmin"]:
        return admin_menu()
    else:
        return user_menu()
