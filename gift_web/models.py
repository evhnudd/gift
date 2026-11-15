"""Модели предметной области «Система учета подарков».

Каждая модель соответствует таблице базы данных ПР7:
users -> User, gifts -> Gift, events -> Event.
"""

from django.db import models
from django.db.models import F, Q
from django.urls import reverse

from gift_web.slugs import make_slug


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
    slug = models.SlugField(
        "слаг",
        max_length=60,
        unique=True,
        help_text="Часть адреса страницы получателя, например anna.",
    )

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        # Если слаг не указан, формируем его из имени.
        if not self.slug:
            taken = set(
                User.objects.exclude(pk=self.pk).values_list("slug", flat=True)
            )
            self.slug = make_slug(self.name, taken)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        """Адрес страницы получателя: /recipients/<slug>/."""
        return reverse("gift_web:recipient_detail", args=[self.slug])


class GiftQuerySet(models.QuerySet):
    """Повторно используемые условия отбора подарков.

    Условия по статусу описаны один раз здесь, а не дублируются
    в представлениях, формах и статистике.
    """

    def active(self):
        """Актуальные подарки: все, кроме отменённых."""
        return self.exclude(status=Gift.Status.CANCELLED)

    def planned(self):
        return self.filter(status=Gift.Status.PLANNED)

    def ordered(self):
        return self.filter(status=Gift.Status.ORDERED)

    def delivered(self):
        return self.filter(status=Gift.Status.DELIVERED)

    def cancelled(self):
        return self.filter(status=Gift.Status.CANCELLED)

    def for_date(self, day):
        """Подарки с доставкой в указанный день."""
        return self.filter(delivery_date=day)

    def within_budget(self, budget):
        """Подарки, полная стоимость которых не превышает бюджет."""
        return self.filter(total_cost__lte=budget)

    def with_recipient(self):
        """Подарки вместе с получателем одним SQL-запросом (JOIN)."""
        return self.select_related("recipient")

    def search(self, text):
        """Поиск по названию подарка или имени получателя."""
        return self.filter(text_search_q(text, "name", "recipient__name"))


class Gift(models.Model):
    """Подарок, запланированный для одного получателя."""

    class Status(models.TextChoices):
        PLANNED = "planned", "Запланирован"
        ORDERED = "ordered", "Заказан"
        DELIVERED = "delivered", "Вручён"
        CANCELLED = "cancelled", "Отменён"

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
    status = models.CharField(
        "статус",
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNED,
    )
    total_cost = models.GeneratedField(
        expression=F("price") + F("delivery_cost"),
        output_field=models.DecimalField(max_digits=11, decimal_places=2),
        db_persist=True,
        verbose_name="итого, руб.",
    )

    image = models.ImageField(
        "фото подарка",
        upload_to="gifts/",
        blank=True,
        help_text="Необязательно. Файл JPG, PNG или WEBP до 2 МБ.",
    )

    objects = GiftQuerySet.as_manager()

    class Meta:
        verbose_name = "подарок"
        verbose_name_plural = "подарки"
        ordering = ["delivery_date", "name"]

    def __str__(self) -> str:
        return self.name

    def get_absolute_url(self) -> str:
        return reverse("gift_web:gift_detail", args=[self.pk])

    @property
    def is_active(self) -> bool:
        return self.status != self.Status.CANCELLED

    def cancel(self) -> None:
        """Отмена подарка: запись сохраняется, меняется только статус."""
        self.status = self.Status.CANCELLED
        self.save(update_fields=["status"])


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
