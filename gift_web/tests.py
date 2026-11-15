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
            is_purchased=True,
        )
        cls.game = Gift.objects.create(
            name="Настольная игра",
            recipient=cls.ivan,
            price=Decimal("1800"),
            delivery_cost=Decimal("250"),
            delivery_date=SOON,
        )
        cls.birthday = Event.objects.create(
            title="День рождения Анны",
            event_date=SOON,
            user=cls.anna,
            gift=cls.headphones,
        )


class ModelTests(BaseData):
    def test_related_objects(self):
        self.assertEqual(self.headphones.recipient.name, "Анна")
        self.assertEqual(self.anna.gifts.count(), 2)
        self.assertEqual(self.anna.events.get().title, "День рождения Анны")

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
            reverse("gift_web:recipient_detail", args=[self.anna.pk]),
            reverse("gift_web:gift_list"),
            reverse("gift_web:gift_detail", args=[self.book.pk]),
            reverse("gift_web:gift_search"),
            reverse("gift_web:event_list"),
            reverse("gift_web:event_detail", args=[self.birthday.pk]),
            reverse("gift_web:statistics"),
        ]
        for url in urls:
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 200)

    def test_missing_objects_return_404(self):
        for url in ("/gifts/999/", "/recipients/999/", "/users/999/"):
            with self.subTest(url=url):
                self.assertEqual(self.client.get(url).status_code, 404)

    def test_user_search_by_name_or_email(self):
        response = self.client.get("/users/?q=ivan@")
        self.assertEqual([u.name for u in response.context["users"]], ["Иван"])


class GiftListTests(BaseData):
    def names(self, query=""):
        response = self.client.get("/gifts/" + query)
        self.assertEqual(response.status_code, 200)
        return [gift["name"] for gift in response.context["gifts"]]

    def test_total_cost_and_status_from_orm(self):
        response = self.client.get("/gifts/?q=книга")
        gift = response.context["gifts"][0]
        self.assertEqual(gift["total_cost"], Decimal("1700"))
        self.assertEqual(gift["status_label"], "Подарок заказан и ожидается")

    def test_filter_by_purchase(self):
        self.assertEqual(self.names("?status=purchased"), ["Книга"])
        self.assertEqual(len(self.names("?status=not_purchased")), 2)

    def test_search_by_recipient_name(self):
        self.assertEqual(self.names("?q=иван"), ["Настольная игра"])

    def test_filter_by_recipient_and_period(self):
        query = f"?recipient={self.anna.pk}&date_from={LATER.isoformat()}"
        self.assertEqual(self.names(query), ["Книга"])

    def test_sort_by_cost_desc(self):
        self.assertEqual(
            self.names("?sort=-cost"), ["Наушники", "Настольная игра", "Книга"]
        )

    def test_bad_parameters_do_not_crash(self):
        response = self.client.get("/gifts/?sort=id;drop&date_from=31-31-2026")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["errors"]), 2)

    @override_settings(GIFTS_PER_PAGE=1)
    def test_pagination_keeps_filters(self):
        response = self.client.get("/gifts/?sort=name&page=2")
        page = response.context["page_obj"]
        self.assertEqual(page.paginator.num_pages, 3)
        self.assertContains(response, "sort=name&amp;page=3")

    def test_budget_search(self):
        response = self.client.get("/gifts/search/?budget=2100")
        names = [gift.name for gift in response.context["gifts"]]
        self.assertEqual(names, ["Книга", "Настольная игра"])


class StatisticsTests(BaseData):
    def test_summary(self):
        response = self.client.get(reverse("gift_web:statistics"))
        summary = response.context["summary"]
        self.assertEqual(summary["gifts_count"], 3)
        self.assertEqual(summary["total_sum"], Decimal("8300"))
        self.assertEqual(summary["purchased"], 1)

    def test_recipients_without_gifts_are_kept(self):
        response = self.client.get(reverse("gift_web:statistics"))
        rows = {
            row.name: row.gifts_count
            for row in response.context["by_recipient"]
        }
        self.assertEqual(rows, {"Анна": 2, "Иван": 1, "Ольга": 0})

    def test_having_threshold(self):
        response = self.client.get("/statistics/?min_gifts=2")
        names = [row.name for row in response.context["active_recipients"]]
        self.assertEqual(names, ["Анна"])
