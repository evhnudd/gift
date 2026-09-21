from datetime import date

from gifts import add_gift, cancel_order, find_gifts, order_gift


def test_add_and_find_gift():
    gifts = {}
    add_gift(gifts, "Книга", "Ольга", 1000, 200, date(2026, 10, 1))

    assert find_gifts(gifts, "ольга")[0]["name"] == "Книга"


def test_order_and_cancel_gift():
    gifts = {}
    gift_id = add_gift(gifts, "Книга", "Ольга", 1000, 200, date(2026, 10, 1))

    assert order_gift(gifts, gift_id)
    assert not order_gift(gifts, gift_id)
    assert cancel_order(gifts, gift_id)
