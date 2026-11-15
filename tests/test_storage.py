from datetime import date

from gifts import Gift
from storage import load_gifts, load_users, save_gifts, save_users
from users import User


def test_gifts_are_saved_and_loaded_as_objects(tmp_path):
    filename = tmp_path / "gifts.json"
    users = [User(1, "Ольга", "olga@example.com")]
    gifts = [
        Gift(
            1,
            "Книга",
            users[0],
            1000,
            200,
            date(2026, 10, 1),
            True,
        )
    ]

    save_gifts(filename, gifts)
    loaded_gifts = load_gifts(filename, users)

    assert isinstance(loaded_gifts[0], Gift)
    assert loaded_gifts[0].name == "Книга"
    assert loaded_gifts[0].delivery_date == date(2026, 10, 1)
    assert loaded_gifts[0].is_purchased
    assert loaded_gifts[0].recipient is users[0]


def test_users_are_saved_and_loaded_as_objects(tmp_path):
    filename = tmp_path / "users.json"
    users = [User(1, "Ольга", "olga@example.com")]

    save_users(filename, users)
    loaded_users = load_users(filename)

    assert isinstance(loaded_users[0], User)
    assert loaded_users[0].name == "Ольга"
    assert loaded_users[0].email == "olga@example.com"
