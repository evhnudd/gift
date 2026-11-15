"""Формы веб-приложения «Система учета подарков».

GiftFilterForm, BudgetForm, EventPeriodForm - обычные формы (forms.Form)
для GET-параметров списков. GiftForm и GiftEditForm - формы на основе
модели (ModelForm) для создания и редактирования подарка.
"""

from datetime import date

from django import forms
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.utils.deconstruct import deconstructible

from gift_web.models import Gift, User

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
DEFAULT_SORT = "date"

STATUS_ACTIVE = ""  # по умолчанию - все, кроме отменённых
STATUS_ALL = "all"


# ---------- Пользовательские валидаторы ----------

def validate_not_only_digits(value: str) -> None:
    """Валидатор-функция: название не может состоять только из цифр."""
    if value.strip().isdigit():
        raise ValidationError(
            "Название подарка не может состоять только из цифр.",
            code="only_digits",
        )


@deconstructible
class MaxFileSizeValidator:
    """Валидатор-класс: ограничение размера загружаемого файла."""

    def __init__(self, max_mb: int):
        self.max_mb = max_mb

    def __call__(self, file) -> None:
        if file and file.size > self.max_mb * 1024 * 1024:
            raise ValidationError(
                f"Размер файла не должен превышать {self.max_mb} МБ.",
                code="file_too_large",
            )

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, MaxFileSizeValidator)
            and self.max_mb == other.max_mb
        )


# ---------- Формы фильтрации (GET) ----------

class GiftFilterForm(forms.Form):
    """Фильтрация, поиск и сортировка списка подарков."""

    q = forms.CharField(
        label="Поиск",
        required=False,
        max_length=100,
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Название или получатель",
            }
        ),
    )
    recipient = forms.ModelChoiceField(
        label="Получатель",
        queryset=User.objects.order_by("name"),
        required=False,
        empty_label="Все получатели",
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    status = forms.ChoiceField(
        label="Статус",
        required=False,
        choices=[
            (STATUS_ACTIVE, "Актуальные"),
            *Gift.Status.choices,
            (STATUS_ALL, "Все, включая отменённые"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        label="Доставка с",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )
    date_to = forms.DateField(
        label="по",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )
    sort = forms.ChoiceField(
        label="Сортировка",
        required=False,
        choices=[
            ("date", "Дата доставки ↑"),
            ("-date", "Дата доставки ↓"),
            ("cost", "Стоимость ↑"),
            ("-cost", "Стоимость ↓"),
            ("name", "Название"),
            ("recipient", "Получатель"),
        ],
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    def clean_q(self) -> str:
        return self.cleaned_data["q"].strip()

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise ValidationError(
                "Начальная дата периода не может быть позже конечной."
            )
        return cleaned_data


class BudgetForm(forms.Form):
    """Подбор подарков по бюджету."""

    budget = forms.DecimalField(
        label="Бюджет, руб.",
        min_value=0,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(
            attrs={"class": "form-control", "step": "0.01"}
        ),
    )


class EventPeriodForm(forms.Form):
    """Отбор событий за период."""

    date_from = forms.DateField(
        label="С",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )
    date_to = forms.DateField(
        label="По",
        required=False,
        widget=forms.DateInput(
            attrs={"type": "date", "class": "form-control"}
        ),
    )

    def clean(self):
        cleaned_data = super().clean()
        date_from = cleaned_data.get("date_from")
        date_to = cleaned_data.get("date_to")
        if date_from and date_to and date_from > date_to:
            raise ValidationError(
                "Начальная дата периода не может быть позже конечной."
            )
        return cleaned_data


# ---------- Формы на основе модели (POST) ----------

class GiftForm(forms.ModelForm):
    """Создание подарка. Статус не выбирается: новый подарок всегда
    «Запланирован», отмена выполняется отдельной кнопкой."""

    class Meta:
        model = Gift
        fields = [
            "name",
            "recipient",
            "price",
            "delivery_cost",
            "delivery_date",
            "image",
        ]
        labels = {
            "name": "Название подарка",
            "delivery_date": "Дата доставки",
        }
        help_texts = {
            "delivery_cost": "Если доставка не нужна, оставьте 0.",
        }
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например, настольная игра",
                }
            ),
            "recipient": forms.Select(attrs={"class": "form-select"}),
            "price": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "delivery_cost": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01"}
            ),
            "delivery_date": forms.DateInput(
                attrs={"type": "date", "class": "form-control"},
                format="%Y-%m-%d",
            ),
            "image": forms.ClearableFileInput(
                attrs={"class": "form-control", "accept": "image/*"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["name"].validators.append(validate_not_only_digits)
        self.fields["price"].validators.append(MinValueValidator(1))
        self.fields["delivery_cost"].validators.append(MinValueValidator(0))
        self.fields["image"].validators.append(MaxFileSizeValidator(2))

    def clean_delivery_date(self) -> date:
        """Дата доставки не может быть в прошлом.

        При редактировании разрешено оставить прежнюю дату, даже если
        она уже прошла (например, у вручённого подарка).
        """
        delivery_date = self.cleaned_data["delivery_date"]
        unchanged = (
            self.instance.pk is not None
            and delivery_date == self.instance.delivery_date
        )
        if delivery_date < date.today() and not unchanged:
            raise ValidationError(
                "Дата доставки не может быть в прошлом.",
                code="past_date",
            )
        return delivery_date

    def clean(self):
        """Проверки, связывающие несколько полей."""
        cleaned_data = super().clean()
        price = cleaned_data.get("price")
        delivery_cost = cleaned_data.get("delivery_cost")
        recipient = cleaned_data.get("recipient")
        delivery_date = cleaned_data.get("delivery_date")

        if (
            price is not None
            and delivery_cost is not None
            and delivery_cost > price
        ):
            self.add_error(
                "delivery_cost",
                "Доставка не может стоить дороже самого подарка.",
            )

        # Правило предметной области: у получателя не может быть двух
        # актуальных подарков с доставкой в один и тот же день.
        # Отменённые подарки не мешают (active()), редактируемый
        # подарок исключается из проверки (exclude(pk=...)).
        if recipient and delivery_date and self.is_status_active():
            conflict = (
                Gift.objects.active()
                .filter(recipient=recipient)
                .for_date(delivery_date)
                .exclude(pk=self.instance.pk)
            )
            if conflict.exists():
                raise ValidationError(
                    f"У получателя «{recipient}» уже есть актуальный "
                    f"подарок на {delivery_date:%d.%m.%Y}. Выберите "
                    "другую дату или отмените прежний подарок.",
                    code="date_conflict",
                )
        return cleaned_data

    def is_status_active(self) -> bool:
        status = self.cleaned_data.get("status", self.instance.status)
        return status != Gift.Status.CANCELLED


class GiftEditForm(GiftForm):
    """Редактирование подарка: дополнительно можно сменить статус
    (кроме отмены - для неё есть отдельная POST-операция)."""

    class Meta(GiftForm.Meta):
        fields = GiftForm.Meta.fields + ["status"]
        widgets = {
            **GiftForm.Meta.widgets,
            "status": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            choice
            for choice in Gift.Status.choices
            if choice[0] != Gift.Status.CANCELLED
        ]
