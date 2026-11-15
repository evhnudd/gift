"""Автотесты веб-части: модели, ORM-запросы и представления.

Тесты создают собственные данные в тестовой базе, поэтому не зависят
от содержимого рабочей базы db.sqlite3.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse

from gift_web.models import Event, Gift, User

TODAY = date.today()
SOON = TODAY + timedelta(days=10)
LATER = TODAY + timedelta(days=40)


class BaseData(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.anna = User.objects.create(name="Анна", email="anna@test.ru")
        cls.ivan = User.objects.create(name="Иван", email="ivan@test.ru")
        cls.olga = User.objects.create(name="Ольга", email="olga@test.ru")
        cls.headphones = Gift.objects.create(
            name="Наушники",
            recipient=cls.anna,
            price=Decimal("4200"),
            delivery_cost=Decimal("350"),
            delivery_date=SOON,
        )
        cls.book = Gift.objects.create(
            name="Книга",
            recipient=cls.anna,
            price=Decimal("1500"),
            delivery_cost=Decimal("200"),
            delivery_date=LATER,
            status=Gift.Status.ORDERED,
        )
        cls.game = Gift.objects.create(
            name="Настольная игра",
            recipient=cls.ivan,
            price=Decimal("1800"),
            delivery_cost=Decimal("250"),
            delivery_date=SOON,
            status=Gift.Status.CANCELLED,
        )
        cls.birthday = Event.objects.create(
            title="День рождения Анны",
            event_date=SOON,
            user=cls.anna,
            gift=cls.headphones,
        )
        cls.party = Event.objects.create(
            title="Праздник Ивана",
            event_date=LATER,
            user=cls.ivan,
            gift=cls.game,
        )


class ModelTests(BaseData):
    def test_generated_total_cost(self):
        gift = Gift.objects.get(pk=self.headphones.pk)
        self.assertEqual(gift.total_cost, Decimal("4550.00"))

    def test_generated_field_recalculated_by_database(self):
        gift = Gift.objects.get(pk=self.book.pk)
        gift.price = Decimal("2000")
        gift.save()
        gift.refresh_from_db()
        self.assertEqual(gift.total_cost, Decimal("2200.00"))

    def test_slug_created_from_name(self):
        self.assertEqual(self.anna.slug, "anna")
        twin = User.objects.create(name="Анна", email="anna2@test.ru")
        self.assertEqual(twin.slug, "anna-2")

    def test_get_absolute_url(self):
        self.assertEqual(self.anna.get_absolute_url(), "/recipients/anna/")

    def test_related_objects(self):
        self.assertEqual(self.headphones.recipient.name, "Анна")
        self.assertEqual(self.anna.gifts.count(), 2)
        self.assertEqual(self.anna.events.get().title, "День рождения Анны")

    def test_queryset_methods(self):
        self.assertEqual(Gift.objects.active().count(), 2)
        self.assertEqual(Gift.objects.cancelled().get(), self.game)
        self.assertEqual(
            set(Gift.objects.for_date(SOON)), {self.headphones, self.game}
        )
        self.assertEqual(
            list(Gift.objects.within_budget(2000)), [self.book]
        )

    def test_protect_on_delete_recipient(self):
        with self.assertRaises(ProtectedError):
            self.anna.delete()

    def test_set_null_on_delete_gift(self):
        self.headphones.delete()
        self.birthday.refresh_from_db()
        self.assertIsNone(self.birthday.gift)


class PageTests(BaseData):
    def test_pages_available(self):
        urls = [
            reverse("gift_web:index"),
            reverse("gift_web:user_list"),
            reverse("gift_web:user_detail", args=[self.anna.pk]),
            reverse("gift_web:recipient_list"),
            self.anna.get_absolute_url(),
            reverse("gift_web:gift_list"),
            reverse("gift_web:gift_detail", args=[self.book.pk]),
            reverse("gift_web:gift_search"),
            reverse("gift_web:event_list"),
            reverse("gift_web:event_detail", args=[self.party.pk]),
            reverse("gift_web:events_need_gift"),
            reverse("gift_web:statistics"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_objects_return_404(self):
        for url in (
            "/gifts/999/",
            "/gifts/999/edit/",
            "/recipients/no-such-slug/",
            "/users/999/",
            "/events/999/",
        ):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_context_processor(self):
        response = self.client.get(reverse("gift_web:index"))
        self.assertEqual(
            response.context["site_name"], "Система учета подарков"
        )
        self.assertEqual(response.context["active_gifts_count"], 2)

    def test_user_search_by_name_or_email(self):
        response = self.client.get("/users/?q=ivan@")
        self.assertEqual([u.name for u in response.context["users"]], ["Иван"])


class GiftListTests(BaseData):
    def names(self, query=""):
        response = self.client.get("/gifts/" + query)
        self.assertEqual(response.status_code, 200)
        return [gift["name"] for gift in response.context["gifts"]]

    def test_default_list_excludes_cancelled(self):
        self.assertEqual(self.names(), ["Наушники", "Книга"])

    def test_filter_by_status_and_all(self):
        self.assertEqual(self.names("?status=cancelled"), ["Настольная игра"])
        self.assertEqual(len(self.names("?status=all")), 3)

    def test_search_by_recipient_name(self):
        self.assertEqual(self.names("?q=иван&status=all"), ["Настольная игра"])

    def test_search_by_gift_name_any_case(self):
        self.assertEqual(self.names("?q=КНИГ"), ["Книга"])

    def test_filter_by_recipient_and_period(self):
        query = f"?recipient={self.anna.pk}&date_from={LATER.isoformat()}"
        self.assertEqual(self.names(query), ["Книга"])

    def test_sort_by_cost_desc(self):
        self.assertEqual(self.names("?sort=-cost"), ["Наушники", "Книга"])

    def test_unknown_sort_and_bad_date_do_not_crash(self):
        response = self.client.get("/gifts/?sort=id;drop&date_from=31-31-2026")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["errors"]), 2)

    def test_period_validation_message(self):
        response = self.client.get(
            f"/gifts/?date_from={LATER.isoformat()}&date_to={SOON.isoformat()}"
        )
        self.assertContains(response, "не может быть позже конечной")

    @override_settings(GIFTS_PER_PAGE=1)
    def test_pagination_keeps_filters(self):
        response = self.client.get("/gifts/?status=all&sort=name&page=2")
        page = response.context["page_obj"]
        self.assertEqual(page.paginator.num_pages, 3)
        # По алфавиту: Книга, Настольная игра, Наушники («с» раньше «у»).
        self.assertEqual(page.object_list[0]["name"], "Настольная игра")
        self.assertContains(response, "status=all&amp;sort=name&amp;page=3")

    def test_budget_search_ignores_cancelled(self):
        response = self.client.get("/gifts/search/?budget=2100")
        names = [gift.name for gift in response.context["gifts"]]
        self.assertEqual(names, ["Книга"])

    def test_budget_search_invalid_value(self):
        response = self.client.get("/gifts/search/?budget=-5")
        self.assertIsNone(response.context["gifts"])
        self.assertContains(response, "не может быть отрицательным")


class StatisticsTests(BaseData):
    def test_summary_counts_only_active(self):
        response = self.client.get(reverse("gift_web:statistics"))
        summary = response.context["summary"]
        self.assertEqual(summary["gifts_count"], 2)
        self.assertEqual(summary["total_sum"], Decimal("6250.00"))
        counts = response.context["status_counts"]
        self.assertEqual(counts["all_count"], 3)
        self.assertEqual(counts["cancelled"], 1)

    def test_recipients_without_gifts_are_kept(self):
        response = self.client.get(reverse("gift_web:statistics"))
        rows = {
            row.name: row.gifts_count
            for row in response.context["by_recipient"]
        }
        self.assertEqual(rows, {"Анна": 2, "Иван": 0, "Ольга": 0})

    def test_having_threshold(self):
        response = self.client.get("/statistics/?min_gifts=2")
        names = [row.name for row in response.context["active_recipients"]]
        self.assertEqual(names, ["Анна"])

    def test_events_need_gift_counts_cancelled_gift(self):
        response = self.client.get(reverse("gift_web:events_need_gift"))
        self.assertEqual(list(response.context["events"]), [self.party])
