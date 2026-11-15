from django.test import TestCase


class GiftWebViewsTests(TestCase):
    def test_main_pages_are_available(self):
        for url in (
            "/",
            "/users/",
            "/recipients/",
            "/gifts/",
            "/gifts/search/",
            "/events/",
            "/statistics/",
        ):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_detail_pages_are_available(self):
        for url in ("/users/1/", "/recipients/1/", "/gifts/1/", "/events/1/"):
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)

    def test_missing_entity_returns_404(self):
        self.assertEqual(self.client.get("/gifts/999/").status_code, 404)


class SqlPagesTests(TestCase):
    """Проверка страниц, данные для которых получены SQL-запросами."""

    def test_gift_list_uses_join_with_users(self):
        response = self.client.get("/gifts/")
        self.assertContains(response, "Беспроводные наушники")
        self.assertContains(response, "Анна")

    def test_gift_list_filters_by_status(self):
        response = self.client.get("/gifts/?status=not_purchased")
        self.assertContains(response, "Термокружка")
        self.assertNotContains(response, "Умная колонка")

    def test_gift_search_by_budget(self):
        response = self.client.get("/gifts/search/?budget=2100")
        self.assertContains(response, "Термокружка")
        self.assertContains(response, "Настольная игра")
        self.assertNotContains(response, "Беспроводные наушники")

    def test_gift_search_empty_result(self):
        response = self.client.get("/gifts/search/?budget=10")
        self.assertContains(response, "не укладывается ни один подарок")

    def test_gift_search_invalid_budget(self):
        response = self.client.get("/gifts/search/?budget=abc")
        self.assertContains(response, "Бюджет должен быть числом")

    def test_sql_injection_is_treated_as_value(self):
        response = self.client.get(
            "/events/",
            {"date_from": "' OR 1=1 --", "date_to": "2026-01-01"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "События не найдены")

    def test_events_filtered_by_period(self):
        response = self.client.get(
            "/events/?date_from=2026-12-01&date_to=2026-12-31"
        )
        self.assertContains(response, "Новый год у Марии")
        self.assertNotContains(response, "День рождения Анны")

    def test_statistics_groups_by_recipient(self):
        response = self.client.get("/statistics/")
        self.assertContains(response, "Мария")
        self.assertEqual(response.context["summary"]["gifts_count"], 6)

    def test_statistics_having_threshold(self):
        response = self.client.get("/statistics/?min_gifts=3")
        names = [
            row["recipient_name"]
            for row in response.context["active_recipients"]
        ]
        self.assertEqual(names, ["Анна"])
