"""Контекстный процессор: общие данные для всех шаблонов проекта."""

from datetime import date

from gift_web.models import Gift


def site_context(request) -> dict:
    """Добавляет в контекст каждого шаблона название сайта, текущий год
    и количество актуальных (не отменённых) подарков для навигации."""
    return {
        "site_name": "Система учета подарков",
        "current_year": date.today().year,
        "active_gifts_count": Gift.objects.active().count(),
    }
