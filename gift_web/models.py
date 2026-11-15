"""Модели предметной области «Система учета подарков».

Каждая модель соответствует таблице базы данных ПР7:
users -> User, gifts -> Gift, events -> Event.
"""

from django.db import models
from django.db.models import Q
from django.urls import reverse


def text_search_q(text: str, *fields: str) -> Q:
    """Условие «text содержится хотя бы в одном из полей».

    SQLite сравнивает без учёта регистра только латиницу, поэтому
    icontains «иван» не находит «Иван». Ищем несколько вариантов
    написания: как введено, строчными, с заглавной и прописными.
    """
    variants = {text, text.lower(), text.capitalize(), text.upper()}
    condition = Q()
    for field in fields:
        for variant in variants:
            condition |= Q(**{f"{field}__icontains": variant})
    return condition


class User(models.Model):
    """Пользователь системы; он же получатель подарков.

    Это модель предметной области, а не встроенный пользователь
    django.contrib.auth: вход в систему она не обеспечивает.
    """

    name = models.CharField("имя", max_length=100)
    email = models.EmailField("электронная почта", unique=True)

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Gift(models.Model):
    """Подарок, запланированный для одного получателя."""

    name = models.CharField("название", max_length=200)
    recipient = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name="gifts",
        verbose_name="получатель",
    )
    price = models.DecimalField(
        "стоимость, руб.",
        max_digits=10,
        decimal_places=2,
    )
    delivery_cost = models.DecimalField(
        "доставка, руб.",
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    delivery_date = models.DateField("дата доставки")
    is_purchased = models.BooleanField("заказан", default=False)

    class Meta:
        verbose_name = "подарок"
        verbose_name_plural = "подарки"
        ordering = ["delivery_date", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("gift_web:gift_detail", args=[self.pk])


class Event(models.Model):
    """Событие календаря, к которому может быть привязан подарок."""

    title = models.CharField("название", max_length=200)
    event_date = models.DateField("дата события")
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="events",
        verbose_name="пользователь",
    )
    gift = models.ForeignKey(
        Gift,
        on_delete=models.SET_NULL,
        related_name="events",
        verbose_name="подарок",
        null=True,
        blank=True,
    )
    description = models.TextField("описание", blank=True)

    class Meta:
        verbose_name = "событие"
        verbose_name_plural = "события"
        ordering = ["event_date"]

    def __str__(self) -> str:
        return f"{self.title} ({self.event_date:%d.%m.%Y})"
