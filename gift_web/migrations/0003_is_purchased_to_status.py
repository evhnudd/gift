"""Миграция данных: перенос признака is_purchased в поле status.

Выполняется ДО удаления is_purchased (миграция 0004), иначе исходные
значения были бы потеряны.

Правила преобразования:
    is_purchased = False                          -> PLANNED (запланирован)
    is_purchased = True, дата доставки не прошла  -> ORDERED (заказан)
    is_purchased = True, дата доставки прошла     -> DELIVERED (вручён)
"""

from datetime import date

from django.db import migrations


def forwards(apps, schema_editor):
    # Используем «историческую» модель из состояния миграций,
    # а не импорт из models.py: структура модели могла измениться позже.
    Gift = apps.get_model("gift_web", "Gift")
    today = date.today()
    Gift.objects.filter(is_purchased=False).update(status="planned")
    Gift.objects.filter(
        is_purchased=True, delivery_date__gte=today
    ).update(status="ordered")
    Gift.objects.filter(
        is_purchased=True, delivery_date__lt=today
    ).update(status="delivered")


def backwards(apps, schema_editor):
    Gift = apps.get_model("gift_web", "Gift")
    Gift.objects.filter(status__in=["ordered", "delivered"]).update(
        is_purchased=True
    )
    Gift.objects.filter(status__in=["planned", "cancelled"]).update(
        is_purchased=False
    )


class Migration(migrations.Migration):

    dependencies = [
        ("gift_web", "0002_gift_status"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
