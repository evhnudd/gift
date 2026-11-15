from pathlib import Path

from gifts import (
    Gifts,
    add_gift,
    calculate_total_cost,
    cancel_order,
    check_gift_budget,
    find_gifts,
    get_budget_status,
    get_gift,
    order_gift,
)
from storage import (
    load_gifts,
    load_settings,
    load_users,
    save_gifts,
    save_users,
)
from users import Users, add_user, get_user
from utils import input_date, input_float, input_int


BUDGET = 5000
DATA_FILE = Path(__file__).parent / "data" / "gifts.json"
USERS_FILE = Path(__file__).parent / "data" / "users.json"
SETTINGS_FILE = Path(__file__).parent / "data" / "settings.json"


def show_gifts(gifts: Gifts) -> None:
    """Выводит список подарков в виде таблицы."""
    if not gifts:
        print("Список подарков пуст.")
        return
    for gift in gifts:
        print(gift)


def show_orders(gifts: Gifts) -> None:
    """Выводит только заказанные подарки."""
    ordered_gifts = [gift for gift in gifts if gift.is_purchased]
    if not ordered_gifts:
        print("Заказанных подарков нет.")
        return
    show_gifts(ordered_gifts)


def show_users(users: Users) -> None:
    """Выводит список пользователей."""
    if not users:
        print("Список пользователей пуст.")
        return
    for user in users:
        print(user)


def main() -> None:
    """Запускает меню управления подарками."""
    users = load_users(USERS_FILE)
    gifts = load_gifts(DATA_FILE, users)
    budget = float(load_settings(SETTINGS_FILE).get("budget", BUDGET))
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
            "8. Показать пользователей\n"
            "9. Добавить пользователя\n"
            "0. Выход"
        )
        choice = input_int("Выберите действие: ")
        if choice == 0:
            save_gifts(DATA_FILE, gifts)
            save_users(USERS_FILE, users)
            print("Данные сохранены.")
            break
        if choice == 1:
            show_gifts(gifts)
        elif choice == 2:
            for gift in find_gifts(gifts, input("Название или получатель: ")):
                print(gift.name, "-", gift.recipient.name)
        elif choice == 3:
            gift_id = input_int("Идентификатор подарка: ")
            try:
                total_cost = calculate_total_cost(
                    get_gift(gifts, gift_id).price,
                    get_gift(gifts, gift_id).delivery_cost,
                )
                print(get_budget_status(total_cost, budget))
                print("Проверка:", check_gift_budget(gifts, gift_id, budget))
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
            try:
                recipient_id = input_int("Идентификатор получателя: ")
                recipient = get_user(users, recipient_id)
                gift = add_gift(
                    gifts,
                    input("Название подарка: "),
                    recipient,
                    input_float("Стоимость: "),
                    input_float("Доставка: "),
                    input_date("Дата доставки (ДД.ММ.ГГГГ): "),
                )
                print(f"Подарок добавлен под номером {gift.id}.")
            except KeyError:
                print("Пользователь не найден.")
        elif choice == 8:
            show_users(users)
        elif choice == 9:
            user = add_user(
                users,
                input("Имя пользователя: "),
                input("Электронная почта: "),
            )
            print(f"Пользователь добавлен под номером {user.id}.")
        else:
            print("Неизвестное действие.")


if __name__ == "__main__":
    main()
