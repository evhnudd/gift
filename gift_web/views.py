"""Представления веб-части.

С ПР9 данные получаются через Django ORM (модели gift_web/models.py),
SQL-запросы через sqlite3 в представлениях больше не используются.
"""

from datetime import date
from decimal import Decimal, InvalidOperation

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import (
    Avg,
    Case,
    CharField,
    Count,
    F,
    Max,
    Min,
    Q,
    Sum,
    Value,
    When,
)
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from gift_web.models import Event, Gift, User, text_search_q

# Разрешённые значения параметра sort -> поля для order_by().
# Пользовательское значение никогда не передаётся в order_by() напрямую.
SORT_FIELDS = {
    "date": ("delivery_date", "name"),
    "-date": ("-delivery_date", "name"),
    "cost": ("total_cost", "name"),
    "-cost": ("-total_cost", "name"),
    "name": ("name",),
    "recipient": ("recipient__name", "delivery_date"),
}
SORT_CHOICES = [
    ("date", "Дата доставки ↑"),
    ("-date", "Дата доставки ↓"),
    ("cost", "Стоимость ↑"),
    ("-cost", "Стоимость ↓"),
    ("name", "Название"),
    ("recipient", "Получатель"),
]
DEFAULT_SORT = "date"

# Полная стоимость считается в SQL: price + delivery_cost.
TOTAL_COST = F("price") + F("delivery_cost")


def status_key():
    """Код статуса для CSS: planned / ordered / delivered."""
    return Case(
        When(is_purchased=False, then=Value("planned")),
        When(delivery_date__gte=date.today(), then=Value("ordered")),
        default=Value("delivered"),
        output_field=CharField(),
    )


def status_label():
    """Текст статуса, как в ПР2–ПР7, вычисляется в SQL (CASE ... WHEN)."""
    return Case(
        When(is_purchased=False, then=Value("Подарок еще не заказан")),
        When(
            delivery_date__gte=date.today(),
            then=Value("Подарок заказан и ожидается"),
        ),
        default=Value("Подарок заказан, но дата доставки прошла"),
        output_field=CharField(),
    )


def gifts_with_details():
    """Подарки с полной стоимостью, именем получателя и статусом."""
    return Gift.objects.annotate(
        total_cost=TOTAL_COST,
        recipient_name=F("recipient__name"),
        status=status_key(),
        status_label=status_label(),
    )


def parse_date(value: str, errors: list[str], label: str):
    """Строка YYYY-MM-DD -> date; при ошибке добавляет сообщение."""
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        errors.append(f"{label}: неверная дата «{value}».")
        return None


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "users_count": User.objects.count(),
        "gifts_count": Gift.objects.count(),
        "events_count": Event.objects.count(),
        # Три ближайших события (срез QuerySet -> LIMIT 3).
        "upcoming_events": Event.objects.filter(
            event_date__gte=date.today()
        ).select_related("user")[:3],
    }
    return render(request, "gift_web/index.html", context)


def user_list(request: HttpRequest) -> HttpResponse:
    query = request.GET.get("q", "").strip()
    users = User.objects.annotate(gifts_count=Count("gifts"))
    if query:
        # Поиск по нескольким полям: имя ИЛИ почта.
        users = users.filter(text_search_q(query, "name", "email"))
    users = users.order_by("name")
    return render(
        request,
        "gift_web/user_list.html",
        {"users": users, "query": query},
    )


def user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    user = get_object_or_404(User, pk=user_id)
    # Обратная связь через related_name="events".
    events = user.events.select_related("gift").order_by("event_date")
    return render(
        request,
        "gift_web/user_detail.html",
        {"user": user, "events": events},
    )


def recipient_list(request: HttpRequest) -> HttpResponse:
    # annotate() выполняет LEFT JOIN: получатели без подарков
    # тоже попадают в список (с количеством 0).
    recipients = User.objects.annotate(
        gifts_count=Count("gifts"),
        total_sum=Sum(F("gifts__price") + F("gifts__delivery_cost")),
    ).order_by("name")
    return render(
        request,
        "gift_web/recipient_list.html",
        {"recipients": recipients},
    )


def recipient_detail(request: HttpRequest, recipient_id: int) -> HttpResponse:
    recipient = get_object_or_404(User, pk=recipient_id)
    gifts = gifts_with_details().filter(recipient=recipient).order_by(
        "delivery_date"
    )
    return render(
        request,
        "gift_web/recipient_detail.html",
        {"recipient": recipient, "gifts": gifts},
    )


def gift_list(request: HttpRequest) -> HttpResponse:
    """Список подарков: фильтрация + поиск + сортировка + пагинация.

    Параметры берутся из request.GET и проверяются вручную.
    """
    errors: list[str] = []
    query = request.GET.get("q", "").strip()
    status = request.GET.get("status", "")
    recipient_id = request.GET.get("recipient", "")
    date_from = parse_date(request.GET.get("date_from", ""), errors, "С")
    date_to = parse_date(request.GET.get("date_to", ""), errors, "По")
    sort = request.GET.get("sort", DEFAULT_SORT)
    if sort not in SORT_FIELDS:
        if sort:
            errors.append("Неизвестный вариант сортировки.")
        sort = DEFAULT_SORT
    if date_from and date_to and date_from > date_to:
        errors.append("Начальная дата периода не может быть позже конечной.")
        date_from = date_to = None

    gifts = Gift.objects.all()
    if status == "purchased":
        gifts = gifts.filter(is_purchased=True)
    elif status == "not_purchased":
        # exclude(): убираем из выборки уже заказанные подарки.
        gifts = gifts.exclude(is_purchased=True)
    else:
        status = ""
    if query:
        gifts = gifts.filter(
            text_search_q(query, "name", "recipient__name")
        )
    if recipient_id.isdigit():
        gifts = gifts.filter(recipient_id=int(recipient_id))
    if date_from:
        gifts = gifts.filter(delivery_date__gte=date_from)
    if date_to:
        gifts = gifts.filter(delivery_date__lte=date_to)

    # values() + annotate(F()) - только нужные поля, данные получателя
    # берутся тем же SQL-запросом через JOIN.
    gifts = (
        gifts.annotate(
            total_cost=TOTAL_COST,
            recipient_name=F("recipient__name"),
            status=status_key(),
            status_label=status_label(),
        )
        .order_by(*SORT_FIELDS[sort])
        .values(
            "id",
            "name",
            "recipient_id",
            "recipient_name",
            "total_cost",
            "delivery_date",
            "status",
            "status_label",
        )
    )

    paginator = Paginator(gifts, settings.GIFTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "gift_web/gift_list.html",
        {
            "page_obj": page_obj,
            "gifts": page_obj.object_list,
            "errors": errors,
            "recipients": User.objects.order_by("name"),
            "sort_choices": SORT_CHOICES,
            "params": {
                "q": query,
                "status": status,
                "recipient": recipient_id,
                "date_from": request.GET.get("date_from", ""),
                "date_to": request.GET.get("date_to", ""),
                "sort": sort,
            },
        },
    )


def gift_detail(request: HttpRequest, gift_id: int) -> HttpResponse:
    # select_related: подарок и получатель - одним запросом с JOIN.
    gift = get_object_or_404(
        gifts_with_details().select_related("recipient"), pk=gift_id
    )
    return render(
        request,
        "gift_web/gift_detail.html",
        {"gift": gift, "events": gift.events.all()},
    )


def gift_search(request: HttpRequest) -> HttpResponse:
    """Подбор подарков, укладывающихся в бюджет."""
    raw_budget = request.GET.get("budget", "").strip()
    error = ""
    gifts = None
    budget = None
    if raw_budget:
        try:
            budget = Decimal(raw_budget.replace(",", "."))
        except InvalidOperation:
            error = "Бюджет должен быть числом."
        else:
            if budget < 0:
                error = "Бюджет не может быть отрицательным."
                budget = None
    if budget is not None:
        gifts = (
            gifts_with_details()
            .filter(total_cost__lte=budget)
            .order_by("total_cost")
        )
    return render(
        request,
        "gift_web/gift_search.html",
        {
            "gifts": gifts,
            "budget": budget,
            "raw_budget": raw_budget,
            "error": error,
        },
    )


def event_list(request: HttpRequest) -> HttpResponse:
    errors: list[str] = []
    date_from = parse_date(request.GET.get("date_from", ""), errors, "С")
    date_to = parse_date(request.GET.get("date_to", ""), errors, "По")
    events = Event.objects.select_related("user", "gift")
    if date_from:
        events = events.filter(event_date__gte=date_from)
    if date_to:
        events = events.filter(event_date__lte=date_to)
    return render(
        request,
        "gift_web/event_list.html",
        {
            "events": events.order_by("event_date"),
            "errors": errors,
            "date_from": request.GET.get("date_from", ""),
            "date_to": request.GET.get("date_to", ""),
        },
    )


def event_detail(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(
        Event.objects.select_related("user", "gift"), pk=event_id
    )
    return render(request, "gift_web/event_detail.html", {"event": event})


def statistics(request: HttpRequest) -> HttpResponse:
    try:
        min_gifts = max(int(request.GET.get("min_gifts", 2)), 1)
    except ValueError:
        min_gifts = 2

    # aggregate(): одна строка сводных показателей.
    summary = Gift.objects.annotate(total_cost=TOTAL_COST).aggregate(
        gifts_count=Count("id"),
        total_sum=Sum("total_cost"),
        average_cost=Avg("total_cost"),
        min_cost=Min("total_cost"),
        max_cost=Max("total_cost"),
        purchased=Count("id", filter=Q(is_purchased=True)),
    )
    # GROUP BY is_purchased: values() + annotate().
    by_status = (
        Gift.objects.values("is_purchased")
        .annotate(gifts_count=Count("id"), total_sum=Sum(TOTAL_COST))
        .order_by("is_purchased")
    )
    # GROUP BY получатель (LEFT JOIN, получатели без подарков - с нулём).
    by_recipient = User.objects.annotate(
        gifts_count=Count("gifts"),
        total_sum=Sum(F("gifts__price") + F("gifts__delivery_cost")),
    ).order_by("-gifts_count", "name")
    # Аналог HAVING: фильтр по аннотированному значению.
    active_recipients = by_recipient.filter(gifts_count__gte=min_gifts)
    top_gifts = (
        Gift.objects.select_related("recipient")
        .annotate(total_cost=TOTAL_COST)
        .order_by("-total_cost")[:3]
    )

    return render(
        request,
        "gift_web/statistics.html",
        {
            "summary": summary,
            "by_status": by_status,
            "by_recipient": by_recipient,
            "active_recipients": active_recipients,
            "min_gifts": min_gifts,
            "top_gifts": top_gifts,
        },
    )
