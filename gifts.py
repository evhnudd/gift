from datetime import date
from typing import Any

from users import User, Users, get_user


class Gift:
    """Подарок, его стоимость, доставка и состояние заказа."""

    def __init__(
        self,
        gift_id: int,
        name: str,
        recipient: User | str,
        price: float,
        delivery_cost: float,
        delivery_date: date,
        is_purchased: bool = False,
    ) -> None:
        self.id = gift_id
        self.name = name
        self.recipient = (
            recipient
            if isinstance(recipient, User)
            else User(0, recipient, "")
        )
        self.price = float(price)
        self.delivery_cost = float(delivery_cost)
        self.delivery_date = delivery_date
        self.is_purchased = is_purchased

    @classmethod
    def from_data(
        cls,
        data: dict[str, Any],
        users: Users | None = None,
    ) -> "Gift":
        """Создает объект Gift из записи JSON."""
        recipient_id = data.get("recipient_id")
        if recipient_id is not None and users is not None:
            recipient = get_user(users, int(recipient_id))
        else:
            recipient = User(
                int(recipient_id or 0),
                str(data.get("recipient", "Неизвестный получатель")),
                "",
            )
        return cls(
            gift_id=int(data["id"]),
            name=str(data["name"]),
            recipient=recipient,
            price=float(data["price"]),
            delivery_cost=float(data["delivery_cost"]),
            delivery_date=date.fromisoformat(str(data["delivery_date"])),
            is_purchased=bool(data.get("is_purchased", False)),
        )

    def to_data(self) -> dict[str, Any]:
        """Преобразует объект в структуру для JSON."""
        return {
            "id": self.id,
            "name": self.name,
            "recipient_id": self.recipient.id,
            "price": self.price,
            "delivery_cost": self.delivery_cost,
            "delivery_date": self.delivery_date.isoformat(),
            "is_purchased": self.is_purchased,
        }

    def total_cost(self) -> float:
        """Возвращает стоимость подарка вместе с доставкой."""
        return self.price + self.delivery_cost

    def is_within_budget(self, budget: float) -> bool:
        """Проверяет, укладывается ли подарок в бюджет."""
        return self.total_cost() <= budget

    def order(self) -> bool:
        """Оформляет заказ, если подарок еще не был заказан."""
        if self.is_purchased:
            return False
        self.is_purchased = True
        return True

    def cancel_order(self) -> bool:
        """Отменяет заказ, если он был оформлен."""
        if not self.is_purchased:
            return False
        self.is_purchased = False
        return True

    def status(self) -> str:
        """Возвращает текущий статус заказа и доставки."""
        return get_gift_status(self.is_purchased, self.delivery_date)

    def __str__(self) -> str:
        return (
            f"{self.id}. {self.name} для {self.recipient.name} | "
            f"{self.total_cost():.2f} руб. | {self.status()}"
        )


Gifts = list[Gift]


def calculate_total_cost(gift_price: float, delivery_cost: float) -> float:
    """Возвращает общую стоимость подарка с доставкой."""
    return float(gift_price) + float(delivery_cost)


def get_budget_status(total_cost: float, budget: float) -> str:
    """Сообщает, укладывается ли подарок в бюджет."""
    if total_cost <= budget:
        return "Подарок укладывается в бюджет"
    return "Подарок превышает бюджет"


def get_gift_status(is_purchased: bool, delivery_date: date) -> str:
    """Определяет текущий статус подарка."""
    if is_purchased and delivery_date >= date.today():
        return "Подарок заказан и ожидается"
    if is_purchased:
        return "Подарок заказан, но дата доставки прошла"
    return "Подарок еще не заказан"


def add_gift(
    gifts: Gifts,
    gift_name: str,
    recipient: User | str,
    gift_price: float,
    delivery_cost: float,
    delivery_date: date,
) -> Gift:
    """Создает подарок, добавляет его в коллекцию и возвращает объект."""
    gift_id = max((gift.id for gift in gifts), default=0) + 1
    gift = Gift(
        gift_id,
        gift_name,
        recipient,
        gift_price,
        delivery_cost,
        delivery_date,
    )
    gifts.append(gift)
    return gift


def find_gifts(gifts: Gifts, query: str) -> list[Gift]:
    """Находит подарки по подстроке названия или получателя."""
    query = query.lower()
    return [
        gift
        for gift in gifts
        if query in gift.name.lower()
        or query in gift.recipient.name.lower()
    ]


def check_gift_budget(gifts: Gifts, gift_id: int, budget: float) -> bool:
    """Проверяет, укладывается ли подарок в переданный бюджет."""
    return get_gift(gifts, gift_id).is_within_budget(budget)


def filter_gifts_by_budget(gifts: Gifts, budget: float) -> list[Gift]:
    """Возвращает подарки, общая стоимость которых не превышает бюджет."""
    return [
        gift
        for gift in gifts
        if gift.is_within_budget(budget)
    ]


def sort_gifts(gifts: Gifts) -> list[Gift]:
    """Возвращает подарки, отсортированные по общей стоимости."""
    return sorted(
        gifts,
        key=Gift.total_cost,
    )


def order_gift(gifts: Gifts, gift_id: int) -> bool:
    """Отмечает подарок как заказанный и возвращает результат операции."""
    return get_gift(gifts, gift_id).order()


def cancel_order(gifts: Gifts, gift_id: int) -> bool:
    """Отменяет заказ подарка и возвращает результат операции."""
    return get_gift(gifts, gift_id).cancel_order()


def get_gift(gifts: Gifts, gift_id: int) -> Gift:
    """Находит подарок по идентификатору или сообщает об отсутствии."""
    for gift in gifts:
        if gift.id == gift_id:
            return gift
    raise KeyError(gift_id)
