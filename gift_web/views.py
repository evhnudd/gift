from pathlib import Path

from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import render

from events import Event
from storage import load_gifts, load_users


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _users():
    return load_users(DATA_DIR / "users.json")


def _gifts():
    return load_gifts(DATA_DIR / "gifts.json", _users())


def _events():
    return Event.load_all(DATA_DIR / "events.json")


def index(request: HttpRequest) -> HttpResponse:
    context = {
        "users_count": len(_users()),
        "gifts_count": len(_gifts()),
        "events_count": len(_events()),
    }
    return render(request, "gift_web/index.html", context)


def user_list(request: HttpRequest) -> HttpResponse:
    return render(request, "gift_web/user_list.html", {"users": _users()})


def user_detail(request: HttpRequest, user_id: int) -> HttpResponse:
    user = next(
        (item for item in _users() if item.id == user_id),
        None,
    )
    if user is None:
        raise Http404("Пользователь не найден")
    return render(request, "gift_web/user_detail.html", {"user": user})


def recipient_list(request: HttpRequest) -> HttpResponse:
    return render(
        request,
        "gift_web/recipient_list.html",
        {"recipients": _users()},
    )


def recipient_detail(request: HttpRequest, recipient_id: int) -> HttpResponse:
    recipient = next(
        (item for item in _users() if item.id == recipient_id),
        None,
    )
    if recipient is None:
        raise Http404("Получатель не найден")
    gifts = [gift for gift in _gifts() if gift.recipient.id == recipient_id]
    return render(
        request,
        "gift_web/recipient_detail.html",
        {"recipient": recipient, "gifts": gifts},
    )


def gift_list(request: HttpRequest) -> HttpResponse:
    return render(request, "gift_web/gift_list.html", {"gifts": _gifts()})


def gift_detail(request: HttpRequest, gift_id: int) -> HttpResponse:
    gift = next((item for item in _gifts() if item.id == gift_id), None)
    if gift is None:
        raise Http404("Подарок не найден")
    return render(request, "gift_web/gift_detail.html", {"gift": gift})


def event_list(request: HttpRequest) -> HttpResponse:
    return render(request, "gift_web/event_list.html", {"events": _events()})


def event_detail(request: HttpRequest, event_id: int) -> HttpResponse:
    event = next((item for item in _events() if item.id == event_id), None)
    if event is None:
        raise Http404("Событие не найдено")
    return render(request, "gift_web/event_detail.html", {"event": event})
