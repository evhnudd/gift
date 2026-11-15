import sqlite3

import pytest

from db.database import fetch_all, get_connection
from db.import_json import DATA_DIR, import_all, load_json


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "gifts.sqlite"
    import_all(path, DATA_DIR)
    return path


def test_schema_contains_tables(db_path):
    conn = get_connection(db_path)
    tables = {
        row[0]
        for row in conn.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table'"
        )
    }
    conn.close()
    assert {"users", "gifts", "events"} <= tables


def test_foreign_keys_are_declared(db_path):
    conn = get_connection(db_path)
    gift_fk = conn.execute("PRAGMA foreign_key_list(gifts)").fetchall()
    event_fk = conn.execute("PRAGMA foreign_key_list(events)").fetchall()
    conn.close()
    assert {row[2] for row in gift_fk} == {"users"}
    assert {row[2] for row in event_fk} == {"users", "gifts"}


def test_import_counts_match_json(db_path):
    queries = {
        "users": "SELECT COUNT(*) FROM users",
        "gifts": "SELECT COUNT(*) FROM gifts",
        "events": "SELECT COUNT(*) FROM events",
    }
    conn = get_connection(db_path)
    for table, sql in queries.items():
        count = conn.execute(sql).fetchone()[0]
        assert count == len(load_json(DATA_DIR / (table + ".json")))
    conn.close()


def test_import_is_repeatable(db_path):
    counts = import_all(db_path, DATA_DIR)
    assert counts["gifts"] == len(load_json(DATA_DIR / "gifts.json"))


def test_foreign_key_violation_is_rejected(db_path):
    conn = get_connection(db_path)
    with pytest.raises(sqlite3.IntegrityError):
        conn.execute(
            "INSERT INTO gifts (name, recipient_id, price, delivery_date) "
            "VALUES (?, ?, ?, ?)",
            ("Ошибка", 999, 100, "2026-12-01"),
        )
    conn.close()


def test_rows_are_accessible_by_name(db_path):
    rows = fetch_all(
        "SELECT name, price + delivery_cost AS total_cost "
        "FROM gifts WHERE price + delivery_cost <= ? ORDER BY total_cost",
        [2100],
        db_path,
    )
    assert [row["name"] for row in rows] == [
        "Термокружка",
        "Книга по фотографии",
        "Настольная игра",
    ]
