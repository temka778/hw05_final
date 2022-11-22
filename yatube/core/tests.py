from http import HTTPStatus

from django.test import TestCase


class ViewTestClass(TestCase):
    def test_page_error(self):
        response = self.client.get("/non-existed_page/")
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertTemplateUsed(response, "core/404.html")
