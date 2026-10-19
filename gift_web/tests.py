from django.test import TestCase


class GiftWebViewsTests(TestCase):
    def test_main_pages_are_available(self):
        for url in ("/", "/users/", "/recipients/", "/gifts/", "/events/"):
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
