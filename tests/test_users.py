from users import User, add_user, find_users


def test_user_creation_and_string_representation():
    user = User(1, "Анна", "anna@example.com")

    assert user.id == 1
    assert user.name == "Анна"
    assert str(user) == "1. Анна (anna@example.com)"


def test_add_and_find_user():
    users: list[User] = []
    user = add_user(users, "Иван", "ivan@example.com")

    assert find_users(users, "иван") == [user]
    assert find_users(users, "example.com") == [user]
