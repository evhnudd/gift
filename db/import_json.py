"""Перенос данных из JSON-файлов ПР1–ПР6 в базу SQLite.

Запуск из корня проекта:
    python -m db.import_json

Скрипт создает таблицы (если их нет), очищает их и заново загружает
данные из data/users.json, data/gifts.json и data/events.json.
Порядок импорта важен: сначала users, затем gifts (ссылаются на users),
затем events (ссылаются на users и gifts).
"""

import json
import sqlite3
from pathlib import Path

from db.database import BASE_DIR, DB_PATH, create_schema, get_connection

DATA_DIR = BASE_DIR / "data"


def load_json(filename: str | Path) -> list[dict]:
    with open(filename, encoding="utf-8") as file:
        return json.load(file)


def clear_tables(conn: sqlite3.Connection) -> None:
    """Удаляет старые записи в порядке, обратном зависимостям."""
    conn.execute("DELETE FROM events")
    conn.execute("DELETE FROM gifts")
    conn.execute("DELETE FROM users")


def import_users(conn: sqlite3.Connection, data_dir: Path) -> int:
    users = load_json(data_dir / "users.json")
    conn.executemany(
        """
        INSERT INTO users (id, name, email)
        VALUES (?, ?, ?)
        """,
        [(user["id"], user["name"], user["email"]) for user in users],
    )
    return len(users)


def import_gifts(conn: sqlite3.Connection, data_dir: Path) -> int:
    gifts = load_json(data_dir / "gifts.json")
    conn.executemany(
        """
        INSERT INTO gifts (
            id,
            name,
            recipient_id,
            price,
            delivery_cost,
            delivery_date,
            is_purchased
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                gift["id"],
                gift["name"],
                gift["recipient_id"],
                float(gift["price"]),
                float(gift["delivery_cost"]),
                gift["delivery_date"],
                int(gift.get("is_purchased", False)),
            )
            for gift in gifts
        ],
    )
    return len(gifts)


def import_events(conn: sqlite3.Connection, data_dir: Path) -> int:
    events = load_json(data_dir / "events.json")
    conn.executemany(
        """
        INSERT INTO events (
            id,
            title,
            event_date,
            user_id,
            gift_id,
            description
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        [
            (
                event["id"],
                event["title"],
                event["event_date"],
                event["user_id"],
                event.get("gift_id"),
                event.get("description") or None,
            )
            for event in events
        ],
    )
    return len(events)


def import_all(
    db_path: str | Path = DB_PATH,
    data_dir: Path = DATA_DIR,
) -> dict[str, int]:
    """Создает схему и переносит все JSON-данные одной транзакцией."""
    conn = get_connection(db_path)
    try:
        create_schema(conn)
        clear_tables(conn)
        counts = {
            "users": import_users(conn, data_dir),
            "gifts": import_gifts(conn, data_dir),
            "events": import_events(conn, data_dir),
        }
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return counts


def main() -> None:
    counts = import_all()
    for table, count in counts.items():
        print(f"{table}: импортировано записей - {count}")


if __name__ == "__main__":
    main()
