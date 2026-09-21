from datetime import date, datetime


def input_int(prompt: str) -> int:
    """Запрашивает целое число и повторяет запрос при ошибке."""
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Введите целое число.")


def input_float(prompt: str) -> float:
    """Запрашивает число с плавающей точкой и повторяет запрос при ошибке."""
    while True:
        try:
            return float(input(prompt).replace(",", "."))
        except ValueError:
            print("Введите число.")


def input_date(prompt: str) -> date:
    """Запрашивает дату в формате ДД.ММ.ГГГГ и повторяет запрос при ошибке."""
    while True:
        try:
            return datetime.strptime(input(prompt), "%d.%m.%Y").date()
        except ValueError:
            print("Введите дату в формате ДД.ММ.ГГГГ.")
