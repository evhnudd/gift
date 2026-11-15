"""Настройка административной панели Django для моделей проекта."""

from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from gift_web.models import Event, Gift, User


class GiftInline(admin.TabularInline):
    """Подарки получателя прямо в карточке пользователя."""

    model = Gift
    fields = ("name", "price", "delivery_cost", "delivery_date", "status")
    extra = 0
    show_change_link = True


class EventInline(admin.TabularInline):
    model = Event
    fk_name = "user"
    fields = ("title", "event_date", "gift")
    extra = 0
    show_change_link = True


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "slug", "gifts_count")
    search_fields = ("name", "email")
    ordering = ("name",)
    list_per_page = 20
    prepopulated_fields = {"slug": ("name",)}
    inlines = (GiftInline, EventInline)

    def get_queryset(self, request):
        # Количество подарков считается в том же SQL-запросе.
        return super().get_queryset(request).annotate(
            gifts_total=Count("gifts")
        )

    @admin.display(description="подарков", ordering="gifts_total")
    def gifts_count(self, obj):
        return obj.gifts_total


@admin.register(Gift)
class GiftAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "recipient",
        "price",
        "delivery_cost",
        "total_cost",
        "delivery_date",
        "status",
        "image_preview",
    )
    list_display_links = ("name",)
    list_editable = ("status",)
    list_filter = ("status", "delivery_date", "recipient")
    search_fields = ("name", "recipient__name", "recipient__email")
    date_hierarchy = "delivery_date"
    ordering = ("delivery_date", "name")
    list_per_page = 20
    list_select_related = ("recipient",)
    autocomplete_fields = ("recipient",)
    readonly_fields = ("total_cost", "image_preview")
    fieldsets = (
        (None, {"fields": ("name", "recipient", "status")}),
        (
            "Стоимость и доставка",
            {
                "fields": (
                    "price",
                    "delivery_cost",
                    "total_cost",
                    "delivery_date",
                )
            },
        ),
        ("Фото", {"fields": ("image", "image_preview")}),
    )
    actions = ("mark_ordered", "mark_cancelled")

    @admin.display(description="фото")
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 60px">', obj.image.url
            )
        return "—"

    @admin.action(description="Отметить как заказанные")
    def mark_ordered(self, request, queryset):
        updated = queryset.exclude(status=Gift.Status.CANCELLED).update(
            status=Gift.Status.ORDERED
        )
        self.message_user(request, f"Отмечено как заказанные: {updated}.")

    @admin.action(description="Отменить выбранные подарки")
    def mark_cancelled(self, request, queryset):
        updated = queryset.update(status=Gift.Status.CANCELLED)
        self.message_user(request, f"Отменено подарков: {updated}.")


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ("title", "event_date", "user", "gift")
    list_filter = ("event_date", "user")
    search_fields = ("title", "user__name", "gift__name")
    date_hierarchy = "event_date"
    ordering = ("event_date",)
    list_per_page = 20
    list_select_related = ("user", "gift")
    autocomplete_fields = ("user", "gift")
