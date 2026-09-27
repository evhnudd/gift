from datetime import date

from gifts import (
    Gift,
    add_gift,
    cancel_order,
    check_gift_budget,
    find_gifts,
    order_gift,
)


def test_add_and_find_gift():
    gifts: list[Gift] = []
    gift = add_gift(
        gifts, "Книга", "Ольга", 1000, 200, date(2026, 10, 1)
    )

    assert gift.name == "Книга"
    assert find_gifts(gifts, "ольга")[0] is gift


def test_order_and_cancel_gift():
    gifts: list[Gift] = []
    gift = add_gift(
        gifts, "Книга", "Ольга", 1000, 200, date(2026, 10, 1)
    )

    assert order_gift(gifts, gift.id)
    assert not order_gift(gifts, gift.id)
    assert cancel_order(gifts, gift.id)


def test_gift_methods_and_string_representation():
    gift = Gift(
        1,
        "Книга",
        "Ольга",
        1000,
        200,
        date(2026, 10, 1),
    )

    assert gift.total_cost() == 1200
    assert gift.is_within_budget(1200)
    assert not gift.is_within_budget(1199)
    assert "Книга для Ольга" in str(gift)


def test_gift_from_data_restores_object():
    gift = Gift.from_data(
        {
            "id": 3,
            "name": "Книга",
            "recipient": "Ольга",
            "price": 1000,
            "delivery_cost": 200,
            "delivery_date": "2026-10-01",
            "is_purchased": True,
        }
    )

    assert gift.id == 3
    assert gift.delivery_date == date(2026, 10, 1)
    assert gift.is_purchased


def test_check_gift_budget_uses_object_state():
    gift = Gift(
        1,
        "Книга",
        "Ольга",
        1000,
        200,
        date(2026, 10, 1),
    )

    assert check_gift_budget([gift], 1, 1200)
    assert not check_gift_budget([gift], 1, 1199)
