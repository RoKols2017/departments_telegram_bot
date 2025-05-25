from datetime import date

def is_valid_personnel_number(text: str) -> bool:
    return text.isdigit() and len(text) == 5

def is_valid_date(text: str) -> bool:
    try:
        day, month, year = map(int, text.split('.'))
        return 1 <= day <= 31 and 1 <= month <= 12 and year > 1900
    except ValueError:
        return False

def parse_date(text: str) -> date | None:
    """
    Парсит строку в формате ДД.ММ.ГГГГ в объект datetime.date
    Возвращает None если формат некорректный
    """
    try:
        day, month, year = map(int, text.strip().split('.'))
        return date(year, month, day)
    except (ValueError, TypeError):
        return None