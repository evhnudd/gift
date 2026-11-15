"""Перенос данных из базы ПР7 (data/gifts.sqlite) в таблицы Django ORM.

Исходная база только читается. Данные записываются через модели
в базу Django (db.sqlite3) с сохранением идентификаторов и связей.

Запуск из корня проекта после `python manage.py migrate`:
    python db/import_sqlite_to_orm.py
"""

import os
import sqlite3
import sys
from datetime import date
from decimal import Decimal
from pathlib import Path

import django

BASE_DIR = Path(__file__).resolve().parent.parent
SOURCE_DB = BASE_DIR / "data" / "gifts.sqlite"

sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gift_project.settings")
django.setup()

from django.db import transaction  # noqa: E402

from gift_web.models import Event, Gift, User  # noqa: E402


def read_rows(connection: sqlite3.Connection, sql: str) -> list[sqlite3.Row]:
    return connection.execute(sql).fetchall()


def to_money(value) -> Decimal:
    """REAL из SQLite -> Decimal с двумя знаками (без хвостов float)."""
    return Decimal(str(value)).quantize(Decimal("0.01"))


@transaction.atomic
def import_data(source_db: Path = SOURCE_DB) -> dict[str, int]:
    """Переносит users -> gifts -> events. Повторный запуск безопасен:
    существующие записи обновляются по id (update_or_create).
    """
    if not source_db.exists():
        raise FileNotFoundError(f"Исходная база не найдена: {source_db}")

    with sqlite3.connect(source_db) as connection:
        connection.row_factory = sqlite3.Row
        users = read_rows(
            connection, "SELECT id, name, email FROM users ORDER BY id"
        )
        gifts = read_rows(
            connection,
            "SELECT id, name, recipient_id, price, delivery_cost, "
            "delivery_date, is_purchased FROM gifts ORDER BY id",
        )
        events = read_rows(
            connection,
            "SELECT id, title, event_date, user_id, gift_id, description "
            "FROM events ORDER BY id",
        )

    for row in users:
        User.objects.update_or_create(
            id=row["id"],
            defaults={"name": row["name"], "email": row["email"]},
        )

    for row in gifts:
        delivery_date = date.fromisoformat(row["delivery_date"])
        Gift.objects.update_or_create(
            id=row["id"],
            defaults={
                "name": row["name"],
                "recipient_id": row["recipient_id"],
                "price": to_money(row["price"]),
                "delivery_cost": to_money(row["delivery_cost"]),
                "delivery_date": delivery_date,
                "is_purchased": bool(row["is_purchased"]),
            },
        )

    for row in events:
        Event.objects.update_or_create(
            id=row["id"],
            defaults={
                "title": row["title"],
                "event_date": date.fromisoformat(row["event_date"]),
                "user_id": row["user_id"],
                "gift_id": row["gift_id"],
                "description": row["description"] or "",
            },
        )

    return {"users": len(users), "gifts": len(gifts), "events": len(events)}


def main() -> None:
    counts = import_data()
    for table, count in counts.items():
        print(f"{table}: перенесено записей - {count}")
    print(
        "В базе Django: "
        f"users={User.objects.count()}, "
        f"gifts={Gift.objects.count()}, "
        f"events={Event.objects.count()}"
    )


if __name__ == "__main__":
    main()
