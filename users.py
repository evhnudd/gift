from typing import Any


class User:
    """Пользователь, для которого планируется подарок."""

    def __init__(self, user_id: int, name: str, email: str) -> None:
        self.id = user_id
        self.name = name
        self.email = email

    @classmethod
    def from_data(cls, data: dict[str, Any]) -> "User":
        """Создает пользователя из записи JSON."""
        return cls(
            user_id=int(data["id"]),
            name=str(data["name"]),
            email=str(data["email"]),
        )

    def to_data(self) -> dict[str, Any]:
        """Преобразует пользователя в структуру для JSON."""
        return {"id": self.id, "name": self.name, "email": self.email}

    def __str__(self) -> str:
        return f"{self.id}. {self.name} ({self.email})"


Users = list[User]


def add_user(users: Users, name: str, email: str) -> User:
    """Создает пользователя, добавляет его в коллекцию и возвращает объект."""
    user_id = max((user.id for user in users), default=0) + 1
    user = User(user_id, name, email)
    users.append(user)
    return user


def find_users(users: Users, query: str) -> list[User]:
    """Находит пользователей по имени или электронной почте."""
    query = query.lower()
    return [
        user
        for user in users
        if query in user.name.lower() or query in user.email.lower()
    ]


def get_user(users: Users, user_id: int) -> User:
    """Находит пользователя по идентификатору."""
    for user in users:
        if user.id == user_id:
            return user
    raise KeyError(user_id)
