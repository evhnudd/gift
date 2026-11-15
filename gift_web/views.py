"""Представления веб-части.

С ПР9 данные получаются через Django ORM (модели gift_web/models.py),
SQL-запросы через sqlite3 в представлениях больше не используются.
ПР11: пользовательский ввод проходит через формы Django (forms.py).
"""

from datetime import date

from django.conf import settings
from django.contrib import messages
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
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from gift_web.forms import (
    DEFAULT_SORT,
    SORT_FIELDS,
    STATUS_ALL,
    BudgetForm,
    EventPeriodForm,
    GiftEditForm,
    GiftFilterForm,
    GiftForm,
)
from gift_web.models import Event, Gift, User, text_search_q

# Условие «подарок не отменён» для агрегатов по связанным подаркам.
ACTIVE_GIFTS = ~Q(gifts__status=Gift.Status.CANCELLED)

# Человекочитаемая подпись статуса, вычисляемая в SQL (CASE ... WHEN).
STATUS_LABEL = Case(
    *[
        When(status=value, then=Value(label))
        for value, label in Gift.Status.choices
    ],
    output_field=CharField(),
)


def gifts_for_cards():
    """Подарки с полями, которые нужны карточке gift_card.html."""
    return Gift.objects.annotate(
        recipient_name=F("recipient__name"),
        recipient_slug=F("recipient__slug"),
        status_label=STATUS_LABEL,
    )


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "users_count": User.objects.count(),
        "gifts_count": Gift.objects.active().count(),
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
        gifts_count=Count("gifts", filter=ACTIVE_GIFTS),
        total_sum=Sum("gifts__total_cost", filter=ACTIVE_GIFTS),
    ).order_by("name")
    return render(
        request,
        "gift_web/recipient_list.html",
        {"recipients": recipients},
    )


def recipient_detail(request: HttpRequest, slug: str) -> HttpResponse:
    recipient = get_object_or_404(User, slug=slug)
    gifts = gifts_for_cards().filter(recipient=recipient).order_by(
        "delivery_date"
    )
    return render(
        request,
        "gift_web/recipient_detail.html",
        {"recipient": recipient, "gifts": gifts},
    )


def gift_list(request: HttpRequest) -> HttpResponse:
    """Список подарков: фильтрация + поиск + сортировка + пагинация."""
    form = GiftFilterForm(request.GET or None)
    gifts = Gift.objects.all()
    sort = DEFAULT_SORT

    if form.is_bound and form.is_valid():
        data = form.cleaned_data
        if data["status"] == STATUS_ALL:
            pass
        elif data["status"]:
            gifts = gifts.filter(status=data["status"])
        else:
            gifts = gifts.active()
        if data["q"]:
            gifts = gifts.search(data["q"])
        if data["recipient"]:
            gifts = gifts.filter(recipient=data["recipient"])
        if data["date_from"]:
            gifts = gifts.filter(delivery_date__gte=data["date_from"])
        if data["date_to"]:
            gifts = gifts.filter(delivery_date__lte=data["date_to"])
        sort = data["sort"] or DEFAULT_SORT
    else:
        # Без параметров или при ошибке в форме - актуальные подарки.
        gifts = gifts.active()

    # values() + annotate(F()) - только нужные поля, данные получателя
    # берутся тем же SQL-запросом через JOIN.
    gifts = (
        gifts.annotate(
            recipient_name=F("recipient__name"),
            recipient_slug=F("recipient__slug"),
            status_label=STATUS_LABEL,
        )
        .order_by(*SORT_FIELDS[sort])
        .values(
            "id",
            "name",
            "recipient_name",
            "recipient_slug",
            "total_cost",
            "delivery_date",
            "status",
            "status_label",
            "image",
        )
    )

    paginator = Paginator(gifts, settings.GIFTS_PER_PAGE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(
        request,
        "gift_web/gift_list.html",
        {"form": form, "page_obj": page_obj, "gifts": page_obj.object_list},
    )


def gift_detail(request: HttpRequest, gift_id: int) -> HttpResponse:
    # select_related: подарок и получатель - одним запросом с JOIN.
    gift = get_object_or_404(
        Gift.objects.select_related("recipient"), pk=gift_id
    )
    return render(
        request,
        "gift_web/gift_detail.html",
        {"gift": gift, "events": gift.events.all()},
    )


def gift_create(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = GiftForm(request.POST, request.FILES)
        if form.is_valid():
            gift = form.save()
            messages.success(request, f"Подарок «{gift}» добавлен.")
            return redirect(gift)
    else:
        initial = {}
        recipient_id = request.GET.get("recipient")
        if recipient_id and recipient_id.isdigit():
            initial["recipient"] = recipient_id
        form = GiftForm(initial=initial)
    return render(
        request,
        "gift_web/gift_form.html",
        {"form": form, "title": "Новый подарок"},
    )


def gift_edit(request: HttpRequest, gift_id: int) -> HttpResponse:
    gift = get_object_or_404(Gift, pk=gift_id)
    if gift.status == Gift.Status.CANCELLED:
        messages.warning(
            request, "Отменённый подарок нельзя редактировать."
        )
        return redirect(gift)
    if request.method == "POST":
        # instance=gift: форма изменяет существующую запись,
        # а не создаёт новую.
        form = GiftEditForm(request.POST, request.FILES, instance=gift)
        if form.is_valid():
            form.save()
            messages.success(request, "Изменения сохранены.")
            return redirect(gift)
    else:
        form = GiftEditForm(instance=gift)
    return render(
        request,
        "gift_web/gift_form.html",
        {"form": form, "gift": gift, "title": f"Редактирование: {gift}"},
    )


@require_POST
def gift_cancel(request: HttpRequest, gift_id: int) -> HttpResponse:
    """Отмена подарка. Только POST: GET-запрос вернёт 405."""
    gift = get_object_or_404(Gift, pk=gift_id)
    if gift.status == Gift.Status.CANCELLED:
        messages.info(request, "Подарок уже отменён.")
    else:
        gift.cancel()
        messages.success(request, f"Подарок «{gift}» отменён.")
    return redirect(gift)


def gift_search(request: HttpRequest) -> HttpResponse:
    """Подбор актуальных подарков, укладывающихся в бюджет."""
    form = BudgetForm(request.GET or None)
    gifts = None
    if form.is_bound and form.is_valid():
        gifts = (
            gifts_for_cards()
            .active()
            .within_budget(form.cleaned_data["budget"])
            .order_by("total_cost")
        )
    return render(
        request,
        "gift_web/gift_search.html",
        {"form": form, "gifts": gifts},
    )


def event_list(request: HttpRequest) -> HttpResponse:
    form = EventPeriodForm(request.GET or None)
    events = Event.objects.select_related("user", "gift")
    if form.is_bound and form.is_valid():
        if form.cleaned_data["date_from"]:
            events = events.filter(
                event_date__gte=form.cleaned_data["date_from"]
            )
        if form.cleaned_data["date_to"]:
            events = events.filter(
                event_date__lte=form.cleaned_data["date_to"]
            )
    return render(
        request,
        "gift_web/event_list.html",
        {"form": form, "events": events.order_by("event_date")},
    )


def event_detail(request: HttpRequest, event_id: int) -> HttpResponse:
    event = get_object_or_404(
        Event.objects.select_related("user", "gift"), pk=event_id
    )
    return render(request, "gift_web/event_detail.html", {"event": event})


def events_need_gift(request: HttpRequest) -> HttpResponse:
    """События, для которых нужно подобрать подарок: подарок не выбран
    или выбранный подарок отменён (отменённый подарок не считается)."""
    events = (
        Event.objects.filter(event_date__gte=date.today())
        .filter(Q(gift__isnull=True) | Q(gift__status=Gift.Status.CANCELLED))
        .select_related("user", "gift")
        .order_by("event_date")
    )
    return render(
        request, "gift_web/events_need_gift.html", {"events": events}
    )


def statistics(request: HttpRequest) -> HttpResponse:
    try:
        min_gifts = max(int(request.GET.get("min_gifts", 2)), 1)
    except ValueError:
        min_gifts = 2

    active = Gift.objects.active()
    # aggregate(): одна строка сводных показателей по актуальным подаркам.
    summary = active.aggregate(
        gifts_count=Count("id"),
        total_sum=Sum("total_cost"),
        average_cost=Avg("total_cost"),
        min_cost=Min("total_cost"),
        max_cost=Max("total_cost"),
    )
    # Условный подсчёт: Count с filter=Q(...) для каждого статуса.
    status_counts = Gift.objects.aggregate(
        all_count=Count("id"),
        planned=Count("id", filter=Q(status=Gift.Status.PLANNED)),
        ordered=Count("id", filter=Q(status=Gift.Status.ORDERED)),
        delivered=Count("id", filter=Q(status=Gift.Status.DELIVERED)),
        cancelled=Count("id", filter=Q(status=Gift.Status.CANCELLED)),
    )
    # GROUP BY status: values() + annotate().
    by_status = (
        Gift.objects.values("status")
        .annotate(
            status_label=STATUS_LABEL,
            gifts_count=Count("id"),
            total_sum=Sum("total_cost"),
        )
        .order_by("status")
    )
    # GROUP BY получатель (LEFT JOIN, получатели без подарков - с нулём).
    by_recipient = User.objects.annotate(
        gifts_count=Count("gifts", filter=ACTIVE_GIFTS),
        total_sum=Sum("gifts__total_cost", filter=ACTIVE_GIFTS),
    ).order_by("-gifts_count", "name")
    # Аналог HAVING: фильтр по аннотированному значению.
    active_recipients = by_recipient.filter(gifts_count__gte=min_gifts)
    top_gifts = active.with_recipient().order_by("-total_cost")[:3]

    return render(
        request,
        "gift_web/statistics.html",
        {
            "summary": summary,
            "status_counts": status_counts,
            "by_status": by_status,
            "by_recipient": by_recipient,
            "active_recipients": active_recipients,
            "min_gifts": min_gifts,
            "top_gifts": top_gifts,
        },
    )
