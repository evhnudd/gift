from datetime import date
from typing import Any


Gift = dict[str, Any]
Gifts = dict[int, Gift]


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
    recipient: str,
    gift_price: float,
    delivery_cost: float,
    delivery_date: date,
) -> int:
    """Добавляет подарок в коллекцию и возвращает его идентификатор."""
    gift_id = max(gifts, default=0) + 1
    gifts[gift_id] = {
        "name": gift_name,
        "recipient": recipient,
        "price": float(gift_price),
        "delivery_cost": float(delivery_cost),
        "delivery_date": delivery_date.isoformat(),
        "is_purchased": False,
    }
    return gift_id


def find_gifts(gifts: Gifts, query: str) -> list[Gift]:
    """Находит подарки по подстроке названия или получателя."""
    query = query.lower()
    return [
        gift
        for gift in gifts.values()
        if query in str(gift["name"]).lower()
        or query in str(gift["recipient"]).lower()
    ]


def check_gift_budget(gifts: Gifts, gift_id: int, budget: float) -> bool:
    """Проверяет, укладывается ли подарок в переданный бюджет."""
    gift = gifts[gift_id]
    total_cost = calculate_total_cost(gift["price"], gift["delivery_cost"])
    return total_cost <= budget


def filter_gifts_by_budget(gifts: Gifts, budget: float) -> list[Gift]:
    """Возвращает подарки, общая стоимость которых не превышает бюджет."""
    return [
        gift
        for gift in gifts.values()
        if calculate_total_cost(
            gift["price"], gift["delivery_cost"]
        ) <= budget
    ]


def sort_gifts(gifts: Gifts) -> list[Gift]:
    """Возвращает подарки, отсортированные по общей стоимости."""
    return sorted(
        gifts.values(),
        key=lambda gift: calculate_total_cost(
            gift["price"], gift["delivery_cost"]
        ),
    )


def order_gift(gifts: Gifts, gift_id: int) -> bool:
    """Отмечает подарок как заказанный и возвращает результат операции."""
    gift = gifts[gift_id]
    if gift["is_purchased"]:
        return False
    gift["is_purchased"] = True
    return True


def cancel_order(gifts: Gifts, gift_id: int) -> bool:
    """Отменяет заказ подарка и возвращает результат операции."""
    gift = gifts[gift_id]
    if not gift["is_purchased"]:
        return False
    gift["is_purchased"] = False
    return True
