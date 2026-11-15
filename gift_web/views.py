"""Представления веб-части.

Начиная с ПР7 данные берутся из базы SQLite data/gifts.sqlite:
представление выполняет SQL-запрос через sqlite3, получает строки
sqlite3.Row и передает их в шаблон через context. Значения от
пользователя подставляются только параметрами ?.
"""

from datetime import date

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import BASE_DIR, fetch_all, fetch_one
from storage import load_settings


# SQL-запросы страниц подарков. Первый параметр ? во всех запросах -
# сегодняшняя дата для вычисления статуса заказа.
GIFTS_SQL = """
        SELECT
            gifts.id,
            gifts.name,
            users.id AS recipient_id,
            users.name AS recipient_name,
            gifts.price,
            gifts.delivery_cost,
            gifts.price + gifts.delivery_cost AS total_cost,
            gifts.delivery_date,
            gifts.is_purchased,
            CASE
                WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= ?
                    THEN 'Подарок заказан и ожидается'
                WHEN gifts.is_purchased = 1
                    THEN 'Подарок заказан, но дата доставки прошла'
                ELSE 'Подарок еще не заказан'
            END AS status
        FROM gifts
        JOIN users
            ON gifts.recipient_id = users.id
        ORDER BY gifts.name;
"""

GIFTS_BY_STATUS_SQL = """
        SELECT
            gifts.id,
            gifts.name,
            users.id AS recipient_id,
            users.name AS recipient_name,
            gifts.price,
            gifts.delivery_cost,
            gifts.price + gifts.delivery_cost AS total_cost,
            gifts.delivery_date,
            gifts.is_purchased,
            CASE
                WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= ?
                    THEN 'Подарок заказан и ожидается'
                WHEN gifts.is_purchased = 1
                    THEN 'Подарок заказан, но дата доставки прошла'
                ELSE 'Подарок еще не заказан'
            END AS status
        FROM gifts
        JOIN users
            ON gifts.recipient_id = users.id
        WHERE gifts.is_purchased = ?
        ORDER BY gifts.name;
"""

GIFT_DETAIL_SQL = """
        SELECT
            gifts.id,
            gifts.name,
            users.id AS recipient_id,
            users.name AS recipient_name,
            gifts.price,
            gifts.delivery_cost,
            gifts.price + gifts.delivery_cost AS total_cost,
            gifts.delivery_date,
            gifts.is_purchased,
            CASE
                WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= ?
                    THEN 'Подарок заказан и ожидается'
                WHEN gifts.is_purchased = 1
                    THEN 'Подарок заказан, но дата доставки прошла'
                ELSE 'Подарок еще не заказан'
            END AS status
        FROM gifts
        JOIN users
            ON gifts.recipient_id = users.id
        WHERE gifts.id = ?;
"""

RECIPIENT_GIFTS_SQL = """
        SELECT
            gifts.id,
            gifts.name,
            users.id AS recipient_id,
            users.name AS recipient_name,
            gifts.price,
            gifts.delivery_cost,
            gifts.price + gifts.delivery_cost AS total_cost,
            gifts.delivery_date,
            gifts.is_purchased,
            CASE
                WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= ?
                    THEN 'Подарок заказан и ожидается'
                WHEN gifts.is_purchased = 1
                    THEN 'Подарок заказан, но дата доставки прошла'
                ELSE 'Подарок еще не заказан'
            END AS status
        FROM gifts
        JOIN users
            ON gifts.recipient_id = users.id
        WHERE users.id = ?
        ORDER BY gifts.name;
"""

GIFTS_WITHIN_BUDGET_SQL = """
        SELECT
            gifts.id,
            gifts.name,
            users.id AS recipient_id,
            users.name AS recipient_name,
            gifts.price,
            gifts.delivery_cost,
            gifts.price + gifts.delivery_cost AS total_cost,
            gifts.delivery_date,
            gifts.is_purchased,
            CASE
                WHEN gifts.is_purchased = 1 AND gifts.delivery_date >= ?
                    THEN 'Подарок заказан и ожидается'
                WHEN gifts.is_purchased = 1
                    THEN 'Подарок заказан, но дата доставки прошла'
                ELSE 'Подарок еще не заказан'
            END AS status
        FROM gifts
        JOIN users
            ON gifts.recipient_id = users.id
        WHERE gifts.price + gifts.delivery_cost <= ?
        ORDER BY total_cost;
"""

EVENTS_SQL = """
        SELECT
            events.id,
            events.title,
            events.event_date,
            users.id AS user_id,
            users.name AS user_name,
            gifts.id AS gift_id,
            gifts.name AS gift_name
        FROM events
        JOIN users
            ON events.user_id = users.id
        LEFT JOIN gifts
            ON events.gift_id = gifts.id
        ORDER BY events.event_date;
"""

EVENTS_IN_PERIOD_SQL = """
        SELECT
            events.id,
            events.title,
            events.event_date,
            users.id AS user_id,
            users.name AS user_name,
            gifts.id AS gift_id,
            gifts.name AS gift_name
        FROM events
        JOIN users
            ON events.user_id = users.id
        LEFT JOIN gifts
            ON events.gift_id = gifts.id
        WHERE events.event_date BETWEEN ? AND ?
        ORDER BY events.event_date;
"""

GIFT_STATUS_FILTERS = {
    "purchased": 1,
    "not_purchased": 0,
}


def _today() -> str:
    return date.today().isoformat()


def _default_budget() -> float:
    settings = load_settings(BASE_DIR / "data" / "settings.json")
    return float(settings.get("budget", 5000))


def index(request: HttpRequest) -> HttpResponse:
    counts = fetch_one(
        """
        SELECT
            (SELECT COUNT(*) FROM users) AS users_count,
            (SELECT COUNT(*) FROM gifts) AS gifts_count,
            (SELECT COUNT(*) FROM events) AS events_count;
        """
    )
    context = {
        "users_count": counts["users_count"],
        "gifts_count": counts["gifts_count"],
        "events_count": counts["events_count"],
    }
    return render(request, "gift_web/index.html", context)


def user_list(request: HttpRequest) -> HttpResponse:
    users = fetch_all(
        """
        SELECT
            id,
            name,
            email
        FROM users
        ORDER BY name;
        """
    )
    return render(request, "gift_web/user_list.html", {"users": users})


def _get_user_or_404(user_id: int, message: str):
    user = fetch_one(
        """
        SELECT
            id,
            name,
            email
        FROM users
        WHERE id = ?;
        """,
        [user_id],
    )
    if user is None:
        raise Http404(message)
    return user


def user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    user = _get_user_or_404(user_id, "Пользователь не найден")
    return render(request, "gift_web/user_detail.html", {"user": user})


def recipient_list(request: HttpRequest) -> HttpResponse:
    recipients = fetch_all(
        """
        SELECT
            users.id,
            users.name,
            COUNT(gifts.id) AS gifts_count,
            COALESCE(SUM(gifts.price + gifts.delivery_cost), 0) AS total_sum
        FROM users
        LEFT JOIN gifts
            ON gifts.recipient_id = users.id
        GROUP BY users.id, users.name
        ORDER BY users.name;
        """
    )
    return render(
        request,
        "gift_web/recipient_list.html",
        {"recipients": recipients},
    )


def recipient_detail(request: HttpRequest, recipient_id: int) -> HttpResponse:
    recipient = _get_user_or_404(recipient_id, "Получатель не найден")
    gifts = fetch_all(RECIPIENT_GIFTS_SQL, [_today(), recipient_id])
    return render(
        request,
        "gift_web/recipient_detail.html",
        {"recipient": recipient, "gifts": gifts},
    )


def gift_list(request: HttpRequest) -> HttpResponse:
    status = request.GET.get("status", "")
    if status in GIFT_STATUS_FILTERS:
        gifts = fetch_all(
            GIFTS_BY_STATUS_SQL,
            [_today(), GIFT_STATUS_FILTERS[status]],
        )
    else:
        status = ""
        gifts = fetch_all(GIFTS_SQL, [_today()])
    return render(
        request,
        "gift_web/gift_list.html",
        {"gifts": gifts, "status": status},
    )


def gift_detail(request: HttpRequest, gift_id: int) -> HttpResponse:
    gift = fetch_one(GIFT_DETAIL_SQL, [_today(), gift_id])
    if gift is None:
        raise Http404("Подарок не найден")
    return render(request, "gift_web/gift_detail.html", {"gift": gift})


def gift_search(request: HttpRequest) -> HttpResponse:
    """Поиск подарков, полная стоимость которых не превышает бюджет."""
    raw_budget = request.GET.get("budget", "").strip()
    error = ""
    gifts = []
    budget = None
    if raw_budget:
        try:
            budget = float(raw_budget.replace(",", "."))
        except ValueError:
            error = "Бюджет должен быть числом."
        else:
            if budget < 0:
                error = "Бюджет не может быть отрицательным."
                budget = None
    if budget is not None:
        gifts = fetch_all(GIFTS_WITHIN_BUDGET_SQL, [_today(), budget])
    return render(
        request,
        "gift_web/gift_search.html",
        {
            "gifts": gifts,
            "budget": budget,
            "raw_budget": raw_budget,
            "default_budget": _default_budget(),
            "error": error,
        },
    )


def event_list(request: HttpRequest) -> HttpResponse:
    date_from = request.GET.get("date_from", "")
    date_to = request.GET.get("date_to", "")
    if date_from and date_to:
        events = fetch_all(EVENTS_IN_PERIOD_SQL, [date_from, date_to])
    else:
        events = fetch_all(EVENTS_SQL)
    return render(
        request,
        "gift_web/event_list.html",
        {"events": events, "date_from": date_from, "date_to": date_to},
    )


def event_detail(request: HttpRequest, event_id: int) -> HttpResponse:
    event = fetch_one(
        """
        SELECT
            events.id,
            events.title,
            events.event_date,
            events.description,
            users.id AS user_id,
            users.name AS user_name,
            gifts.id AS gift_id,
            gifts.name AS gift_name
        FROM events
        JOIN users
            ON events.user_id = users.id
        LEFT JOIN gifts
            ON events.gift_id = gifts.id
        WHERE events.id = ?;
        """,
        [event_id],
    )
    if event is None:
        raise Http404("Событие не найдено")
    return render(request, "gift_web/event_detail.html", {"event": event})


def statistics(request: HttpRequest) -> HttpResponse:
    try:
        min_gifts = max(int(request.GET.get("min_gifts", 2)), 1)
    except ValueError:
        min_gifts = 2
    summary = fetch_one(
        """
        SELECT
            COUNT(*) AS gifts_count,
            COALESCE(SUM(price + delivery_cost), 0) AS total_sum,
            COALESCE(ROUND(AVG(price + delivery_cost), 2), 0) AS average_cost,
            COALESCE(MIN(price + delivery_cost), 0) AS min_cost,
            COALESCE(MAX(price + delivery_cost), 0) AS max_cost
        FROM gifts;
        """
    )
    by_recipient = fetch_all(
        """
        SELECT
            users.id,
            users.name AS recipient_name,
            COUNT(gifts.id) AS gifts_count,
            COALESCE(SUM(gifts.price + gifts.delivery_cost), 0) AS total_sum
        FROM users
        LEFT JOIN gifts
            ON gifts.recipient_id = users.id
        GROUP BY users.id, users.name
        ORDER BY gifts_count DESC, users.name;
        """
    )
    by_status = fetch_all(
        """
        SELECT
            is_purchased,
            COUNT(*) AS gifts_count,
            SUM(price + delivery_cost) AS total_sum
        FROM gifts
        GROUP BY is_purchased
        ORDER BY is_purchased;
        """
    )
    active_recipients = fetch_all(
        """
        SELECT
            users.id,
            users.name AS recipient_name,
            COUNT(gifts.id) AS gifts_count
        FROM users
        JOIN gifts
            ON gifts.recipient_id = users.id
        GROUP BY users.id, users.name
        HAVING COUNT(gifts.id) >= ?
        ORDER BY gifts_count DESC;
        """,
        [min_gifts],
    )
    top_gifts = fetch_all(
        """
        SELECT
            id,
            name,
            price + delivery_cost AS total_cost
        FROM gifts
        ORDER BY total_cost DESC
        LIMIT 3;
        """
    )
    return render(
        request,
        "gift_web/statistics.html",
        {
            "summary": summary,
            "by_recipient": by_recipient,
            "by_status": by_status,
            "active_recipients": active_recipients,
            "min_gifts": min_gifts,
            "top_gifts": top_gifts,
        },
    )
