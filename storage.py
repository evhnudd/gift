import json
from datetime import date
from pathlib import Path
from typing import Any

from gifts import Gift, Gifts
from users import User, Users


def load_gifts(
    filename: str | Path,
    users: Users | None = None,
) -> Gifts:
    """Загружает подарки из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

    return [Gift.from_data(gift, users) for gift in data]


def save_gifts(filename: str | Path, gifts: Gifts) -> None:
    """Сохраняет подарки в JSON-файл."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [gift.to_data() for gift in gifts]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def parse_delivery_date(gift: Gift | dict) -> date:
    """Преобразует дату доставки из записи JSON в объект date."""
    if isinstance(gift, Gift):
        return gift.delivery_date
    return date.fromisoformat(gift["delivery_date"])


def load_users(filename: str | Path) -> Users:
    """Загружает пользователей из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []
    return [User.from_data(user) for user in data]


def save_users(filename: str | Path, users: Users) -> None:
    """Сохраняет пользователей в JSON-файл."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [user.to_data() for user in users]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_settings(filename: str | Path) -> dict[str, Any]:
    """Загружает настройки приложения из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}
