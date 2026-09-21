import json
from datetime import date
from pathlib import Path

from gifts import Gifts


def load_gifts(filename: str | Path) -> Gifts:
    """Загружает подарки из JSON-файла."""
    try:
        with open(filename, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

    return {int(gift["id"]): gift for gift in data}


def save_gifts(filename: str | Path, gifts: Gifts) -> None:
    """Сохраняет подарки в JSON-файл."""
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = [{"id": gift_id, **gift} for gift_id, gift in gifts.items()]
    with open(path, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def parse_delivery_date(gift: dict) -> date:
    """Преобразует дату доставки из записи JSON в объект date."""
    return date.fromisoformat(gift["delivery_date"])
