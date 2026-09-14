from datetime import date


BUDGET = 5000


def calculate_total_cost(gift_price, delivery_cost):
    """Возвращает общую стоимость подарка с доставкой."""
    return float(gift_price) + float(delivery_cost)


def get_budget_status(total_cost, budget):
    """Сообщает, укладывается ли подарок в бюджет."""
    if total_cost <= budget:
        return "Подарок укладывается в бюджет"
    return "Подарок превышает бюджет"


def get_gift_status(is_purchased, delivery_date):
    """Определяет текущий статус подарка."""
    if is_purchased and delivery_date >= date.today():
        return "Подарок заказан и ожидается"
    if is_purchased:
        return "Подарок заказан, но дата доставки прошла"
    return "Подарок еще не заказан"


def main():
    recipient = "Анна"
    gift_name = "Беспроводные наушники"
    gift_price = 4200
    delivery_cost = 350
    is_purchased = True
    delivery_date = date(2026, 9, 20)

    total_cost = calculate_total_cost(gift_price, delivery_cost)

    print("Система учета подарков")
    print(f"Получатель: {recipient}")
    print(f"Подарок: {gift_name}")
    print(f"Стоимость: {total_cost} руб.")
    print(get_budget_status(total_cost, BUDGET))
    print(get_gift_status(is_purchased, delivery_date))


if __name__ == "__main__":
    main()
