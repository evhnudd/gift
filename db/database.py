"""Подключение к базе данных SQLite системы учета подарков."""

import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "data" / "gifts.sqlite"
SCHEMA_PATH = BASE_DIR / "sql" / "schema.sql"


def get_connection(
    db_path: str | Path = DB_PATH,
    named_rows: bool = False,
) -> sqlite3.Connection:
    """Открывает соединение и включает проверку внешних ключей.

    При named_rows=True строки результата возвращаются как sqlite3.Row,
    и к полям можно обращаться по именам: row["name"], {{ row.name }}.
    """
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    if named_rows:
        conn.row_factory = sqlite3.Row
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    """Создает таблицы, выполняя команды из sql/schema.sql."""
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    conn.executescript(sql)
    conn.commit()


def fetch_all(
    sql: str,
    params: tuple | list = (),
    db_path: str | Path = DB_PATH,
) -> list[sqlite3.Row]:
    """Выполняет SELECT и возвращает все строки как sqlite3.Row."""
    conn = get_connection(db_path, named_rows=True)
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def fetch_one(
    sql: str,
    params: tuple | list = (),
    db_path: str | Path = DB_PATH,
) -> sqlite3.Row | None:
    """Выполняет SELECT и возвращает первую строку или None."""
    conn = get_connection(db_path, named_rows=True)
    try:
        return conn.execute(sql, params).fetchone()
    finally:
        conn.close()
