"""Автотесты веб-части: модели, ORM-запросы, представления и формы.

Тесты создают собственные данные в тестовой базе, поэтому не зависят
от содержимого рабочей базы db.sqlite3.
"""

import shutil
import tempfile
from datetime import date, timedelta
from decimal import Decimal
from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from django.test import TestCase, override_settings
from django.urls import reverse
from PIL import Image

from gift_web.forms import GiftForm
from gift_web.models import Event, Gift, User

TODAY = date.today()
SOON = TODAY + timedelta(days=10)
LATER = TODAY + timedelta(days=40)


def make_png() -> bytes:
    """Небольшое корректное PNG-изображение для проверки загрузки."""
    buffer = BytesIO()
    Image.new("RGB", (10, 10), "red").save(buffer, format="PNG")
    return buffer.getvalue()


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

    def test_cancel_keeps_record(self):
        self.headphones.cancel()
        gift = Gift.objects.get(pk=self.headphones.pk)
        self.assertEqual(gift.status, Gift.Status.CANCELLED)

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
        self.assertTrue(response.context["form"].errors)

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
        self.assertTrue(response.context["form"].errors)


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


class GiftFormTests(BaseData):
    def form_data(self, **overrides):
        data = {
            "name": "Термокружка",
            "recipient": self.olga.pk,
            "price": "900",
            "delivery_cost": "150",
            "delivery_date": SOON.isoformat(),
        }
        data.update(overrides)
        return data

    def test_valid_form(self):
        self.assertTrue(GiftForm(data=self.form_data()).is_valid())

    def test_past_date_rejected(self):
        form = GiftForm(data=self.form_data(delivery_date="2020-01-01"))
        self.assertIn("delivery_date", form.errors)

    def test_only_digits_name_rejected(self):
        form = GiftForm(data=self.form_data(name="12345"))
        self.assertIn("name", form.errors)

    def test_delivery_more_expensive_than_gift(self):
        form = GiftForm(data=self.form_data(delivery_cost="1000"))
        self.assertIn("delivery_cost", form.errors)

    def test_conflict_with_active_gift(self):
        form = GiftForm(data=self.form_data(recipient=self.anna.pk))
        self.assertFalse(form.is_valid())
        self.assertIn("уже есть актуальный", str(form.non_field_errors()))

    def test_cancelled_gift_does_not_block_date(self):
        form = GiftForm(data=self.form_data(recipient=self.ivan.pk))
        self.assertTrue(form.is_valid(), form.errors)


class GiftCrudViewTests(BaseData):
    def test_create_gift(self):
        response = self.client.post(
            reverse("gift_web:gift_create"),
            {
                "name": "Термокружка",
                "recipient": self.olga.pk,
                "price": "900",
                "delivery_cost": "150",
                "delivery_date": SOON.isoformat(),
            },
        )
        gift = Gift.objects.get(name="Термокружка")
        self.assertRedirects(response, gift.get_absolute_url())
        self.assertEqual(gift.status, Gift.Status.PLANNED)

    def test_invalid_post_shows_errors_and_saves_nothing(self):
        response = self.client.post(
            reverse("gift_web:gift_create"),
            {"name": "", "recipient": self.olga.pk, "price": "abc"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(Gift.objects.count(), 3)

    def test_edit_does_not_conflict_with_itself(self):
        url = reverse("gift_web:gift_edit", args=[self.headphones.pk])
        response = self.client.post(
            url,
            {
                "name": "Наушники Pro",
                "recipient": self.anna.pk,
                "price": "4200",
                "delivery_cost": "350",
                "delivery_date": SOON.isoformat(),
                "status": Gift.Status.ORDERED,
            },
        )
        self.assertRedirects(response, self.headphones.get_absolute_url())
        self.headphones.refresh_from_db()
        self.assertEqual(self.headphones.name, "Наушники Pro")
        self.assertEqual(Gift.objects.count(), 3)

    def test_edit_conflict_with_other_gift(self):
        url = reverse("gift_web:gift_edit", args=[self.book.pk])
        response = self.client.post(
            url,
            {
                "name": "Книга",
                "recipient": self.anna.pk,
                "price": "1500",
                "delivery_cost": "200",
                "delivery_date": SOON.isoformat(),
                "status": Gift.Status.ORDERED,
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "уже есть актуальный")

    def test_cancel_requires_post(self):
        url = reverse("gift_web:gift_cancel", args=[self.headphones.pk])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.headphones.refresh_from_db()
        self.assertEqual(self.headphones.status, Gift.Status.PLANNED)

    def test_cancel_changes_status(self):
        url = reverse("gift_web:gift_cancel", args=[self.headphones.pk])
        response = self.client.post(url)
        self.assertRedirects(response, self.headphones.get_absolute_url())
        self.headphones.refresh_from_db()
        self.assertEqual(self.headphones.status, Gift.Status.CANCELLED)

    def test_cancelled_gift_cannot_be_edited(self):
        url = reverse("gift_web:gift_edit", args=[self.game.pk])
        response = self.client.get(url)
        self.assertRedirects(response, self.game.get_absolute_url())


class ImageUploadTests(BaseData):
    def setUp(self):
        self.media_dir = tempfile.mkdtemp()
        self.override = override_settings(MEDIA_ROOT=self.media_dir)
        self.override.enable()

    def tearDown(self):
        self.override.disable()
        shutil.rmtree(self.media_dir, ignore_errors=True)

    def test_upload_image(self):
        image = SimpleUploadedFile("photo.png", make_png(), "image/png")
        url = reverse("gift_web:gift_edit", args=[self.book.pk])
        self.client.post(
            url,
            {
                "name": "Книга",
                "recipient": self.anna.pk,
                "price": "1500",
                "delivery_cost": "200",
                "delivery_date": LATER.isoformat(),
                "status": Gift.Status.ORDERED,
                "image": image,
            },
        )
        self.book.refresh_from_db()
        self.assertTrue(self.book.image.name.startswith("gifts/"))
        response = self.client.get(self.book.get_absolute_url())
        self.assertContains(response, self.book.image.url)

    def test_not_an_image_rejected(self):
        fake = SimpleUploadedFile("photo.png", b"not image", "image/png")
        form = GiftForm(
            data={
                "name": "Термокружка",
                "recipient": self.olga.pk,
                "price": "900",
                "delivery_cost": "150",
                "delivery_date": SOON.isoformat(),
            },
            files={"image": fake},
        )
        self.assertIn("image", form.errors)
