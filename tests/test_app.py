"""確認應用程式可建立並顯示繁體中文首頁。"""

import unittest

from app import create_app


class AppSmokeTests(unittest.TestCase):
    def setUp(self):
        self.app = create_app({"TESTING": True})
        self.client = self.app.test_client()

    def test_homepage(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)
        html = response.get_data(as_text=True)
        self.assertIn('lang="zh-Hant"', html)
        self.assertIn("歡迎使用 Mini Moodle", html)
        self.assertIn("上述功能皆尚未實作", html)
        self.assertIn("/static/css/style.css", html)

    def test_stylesheet(self):
        response = self.client.get("/static/css/style.css")
        try:
            self.assertEqual(response.status_code, 200)
            self.assertIn("text/css", response.content_type)
            self.assertIn(".welcome-panel", response.get_data(as_text=True))
        finally:
            response.close()
