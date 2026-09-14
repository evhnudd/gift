from datetime import date

from main import calculate_total_cost, get_budget_status, get_gift_status


def test_calculate_total_cost():
    assert calculate_total_cost(4200, 350) == 4550


def test_get_budget_status():
    assert get_budget_status(4550, 5000) == "Подарок укладывается в бюджет"
    assert get_budget_status(5500, 5000) == "Подарок превышает бюджет"


def test_get_gift_status():
    assert get_gift_status(False, date(2026, 9, 20)) == "Подарок еще не заказан"
    assert get_gift_status(True, date(2026, 9, 20)) == "Подарок заказан и ожидается"
