from pathlib import Path

from gifts import (
    Gifts,
    add_gift,
    calculate_total_cost,
    cancel_order,
    check_gift_budget,
    find_gifts,
    get_budget_status,
    get_gift_status,
    order_gift,
)
from storage import load_gifts, parse_delivery_date, save_gifts
from utils import input_date, input_float, input_int


BUDGET = 5000
DATA_FILE = Path(__file__).parent / "data" / "gifts.json"


def show_gifts(gifts: Gifts) -> None:
    """Выводит список подарков в виде таблицы."""
    if not gifts:
        print("Список подарков пуст.")
        return
    for gift_id, gift in gifts.items():
        total_cost = calculate_total_cost(gift["price"], gift["delivery_cost"])
        status = get_gift_status(
            gift["is_purchased"], parse_delivery_date(gift)
        )
        print(
            f"{gift_id}. {gift['name']} для {gift['recipient']} | "
            f"{total_cost:.2f} руб. | {status}"
        )


def show_orders(gifts: Gifts) -> None:
    """Выводит только заказанные подарки."""
    ordered_gifts = {
        gift_id: gift
        for gift_id, gift in gifts.items()
        if gift["is_purchased"]
    }
    if not ordered_gifts:
        print("Заказанных подарков нет.")
        return
    show_gifts(ordered_gifts)


def main() -> None:
    """Запускает меню управления подарками."""
    gifts = load_gifts(DATA_FILE)
    while True:
        print(
            "\n=== Система учета подарков ===\n"
            "1. Показать подарки\n"
            "2. Найти подарок\n"
            "3. Проверить бюджет\n"
            "4. Заказать подарок\n"
            "5. Отменить заказ\n"
            "6. Показать заказы\n"
            "7. Добавить подарок\n"
            "0. Выход"
        )
        choice = input_int("Выберите действие: ")
        if choice == 0:
            save_gifts(DATA_FILE, gifts)
            print("Данные сохранены.")
            break
        if choice == 1:
            show_gifts(gifts)
        elif choice == 2:
            for gift in find_gifts(gifts, input("Название или получатель: ")):
                print(gift["name"], "-", gift["recipient"])
        elif choice == 3:
            gift_id = input_int("Идентификатор подарка: ")
            try:
                total_cost = calculate_total_cost(
                    gifts[gift_id]["price"], gifts[gift_id]["delivery_cost"]
                )
                print(get_budget_status(total_cost, BUDGET))
                print("Проверка:", check_gift_budget(gifts, gift_id, BUDGET))
            except KeyError:
                print("Подарок не найден.")
        elif choice == 4:
            try:
                gift_id = input_int("Идентификатор подарка: ")
                print(
                    "Заказ создан." if order_gift(gifts, gift_id)
                    else "Подарок уже заказан."
                )
            except KeyError:
                print("Подарок не найден.")
        elif choice == 5:
            try:
                gift_id = input_int("Идентификатор подарка: ")
                print(
                    "Заказ отменен." if cancel_order(gifts, gift_id)
                    else "Подарок не был заказан."
                )
            except KeyError:
                print("Подарок не найден.")
        elif choice == 6:
            show_orders(gifts)
        elif choice == 7:
            gift_id = add_gift(
                gifts,
                input("Название подарка: "),
                input("Получатель: "),
                input_float("Стоимость: "),
                input_float("Доставка: "),
                input_date("Дата доставки (ДД.ММ.ГГГГ): "),
            )
            print(f"Подарок добавлен под номером {gift_id}.")
        else:
            print("Неизвестное действие.")


if __name__ == "__main__":
    main()
