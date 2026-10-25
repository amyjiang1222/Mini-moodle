"""End-to-end checks for the agreed Mini Moodle user stories."""

import re
import tempfile
import unittest
from pathlib import Path

from app import create_app
from app.models import create_user, get_db


class AppStoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
        })
        self.client = self.app.test_client()
        with self.app.app_context():
            create_user("teacher", "teacher-pass", "teacher")
            create_user("other-teacher", "other-pass", "teacher")
            create_user("student", "student-pass", "student")
            create_user("outsider", "outsider-pass", "student")

    def tearDown(self):
        self.tempdir.cleanup()

    def csrf(self, client, path="/"):
        html = client.get(path).get_data(as_text=True)
        return re.search(r'name="csrf_token" value="([^"]+)"', html).group(1)

    def login(self, client, username, password):
        token = self.csrf(client, "/login")
        return client.post("/login", data={
            "username": username, "password": password, "csrf_token": token
        }, follow_redirects=True)

    def create_course(self):
        self.login(self.client, "teacher", "teacher-pass")
        response = self.client.post("/courses/new", data={
            "name": "軟體工程", "description": "需求分析", "csrf_token": self.csrf(self.client)
        })
        self.assertEqual(response.status_code, 302)
        return int(response.headers["Location"].split("/")[-1])

    def test_homepage_and_stylesheet(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("text/html", response.content_type)
        html = response.get_data(as_text=True)
        self.assertIn('lang="zh-Hant"', html)
        self.assertIn("歡迎使用 Mini Moodle", html)
        self.assertIn("請先登入", html)
        css = self.client.get("/static/css/style.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn(".welcome-panel", css.get_data(as_text=True))
        css.close()

    def test_login_roles_and_invalid_credentials(self):
        invalid = self.login(self.client, "teacher", "wrong")
        self.assertIn("帳號或密碼錯誤", invalid.get_data(as_text=True))
        self.assertEqual(self.client.get("/courses/new").status_code, 302)
        self.login(self.client, "student", "student-pass")
        self.assertIn("學生", self.client.get("/").get_data(as_text=True))
        self.assertEqual(self.client.get("/courses/new").status_code, 403)
        self.assertEqual(self.client.post("/courses/new", data={}).status_code, 400)

    def test_course_enrollment_announcements_and_messages(self):
        course_id = self.create_course()
        with self.app.app_context():
            code = get_db().execute(
                "SELECT code FROM courses WHERE id = ?", (course_id,)
            ).fetchone()["code"]
        self.assertRegex(code, r"^[A-Z]{2}[0-9]{7}$")
        detail_url = f"/courses/{course_id}"
        self.assertIn(code, self.client.get(detail_url).get_data(as_text=True))

        token = self.csrf(self.client, detail_url)
        self.client.post(f"{detail_url}/announcements", data={
            "title": "課堂通知", "body": "下週上課", "csrf_token": token
        })
        self.client.post(f"{detail_url}/messages", data={
            "body": "教師留言", "csrf_token": token
        })

        student = self.app.test_client()
        self.login(student, "student", "student-pass")
        self.assertEqual(student.get(detail_url).status_code, 404)
        invalid = student.post("/courses/join", data={
            "code": "ZZ0000000", "csrf_token": self.csrf(student)
        }, follow_redirects=True)
        self.assertIn("找不到這個課碼", invalid.get_data(as_text=True))
        join = student.post("/courses/join", data={
            "code": code.lower(), "csrf_token": self.csrf(student)
        })
        self.assertEqual(join.status_code, 302)
        repeat = student.post("/courses/join", data={
            "code": code, "csrf_token": self.csrf(student)
        }, follow_redirects=True)
        self.assertIn("你已加入這門課程", repeat.get_data(as_text=True))
        with self.app.app_context():
            count = get_db().execute(
                "SELECT count(*) FROM enrollments WHERE course_id = ?", (course_id,)
            ).fetchone()[0]
            self.assertEqual(count, 1)
        student_html = student.get(detail_url).get_data(as_text=True)
        self.assertIn("課堂通知", student_html)
        self.assertIn("教師留言", student_html)
        self.assertNotIn("發布公告</button>", student_html)
        self.assertEqual(student.post(f"{detail_url}/announcements", data={
            "title": "偽公告", "body": "不可發布", "csrf_token": self.csrf(student)
        }).status_code, 403)
        student.post(f"{detail_url}/messages", data={
            "body": "學生留言", "csrf_token": self.csrf(student)
        })
        self.assertIn("學生留言", self.client.get(detail_url).get_data(as_text=True))

        outsider = self.app.test_client()
        self.login(outsider, "outsider", "outsider-pass")
        self.assertEqual(outsider.get(detail_url).status_code, 404)
        self.assertEqual(outsider.post(f"{detail_url}/messages", data={
            "body": "不可留言", "csrf_token": self.csrf(outsider)
        }).status_code, 404)

    def test_blank_inputs_and_other_teacher_cannot_edit(self):
        self.login(self.client, "teacher", "teacher-pass")
        blank = self.client.post("/courses/new", data={
            "name": "   ", "csrf_token": self.csrf(self.client)
        }, follow_redirects=True)
        self.assertIn("課程名稱不可空白", blank.get_data(as_text=True))
        course_id = self.create_course()
        detail_url = f"/courses/{course_id}"
        self.client.post(f"{detail_url}/messages", data={
            "body": "  ", "csrf_token": self.csrf(self.client, detail_url)
        })
        with self.app.app_context():
            count = get_db().execute("SELECT count(*) FROM messages").fetchone()[0]
        self.assertEqual(count, 0)

        other = self.app.test_client()
        self.login(other, "other-teacher", "other-pass")
        self.assertEqual(other.get(detail_url).status_code, 404)
        self.assertEqual(other.post(f"{detail_url}/announcements", data={
            "title": "偽公告", "body": "不可發布", "csrf_token": self.csrf(other)
        }).status_code, 404)

    def test_announcement_edit_is_teacher_only(self):
        course_id = self.create_course()
        detail_url = f"/courses/{course_id}"
        self.client.post(f"{detail_url}/announcements", data={
            "title": "原公告", "body": "原內容", "csrf_token": self.csrf(self.client)
        })
        with self.app.app_context():
            announcement_id = get_db().execute(
                "SELECT id FROM announcements WHERE course_id = ?", (course_id,)
            ).fetchone()["id"]
            code = get_db().execute(
                "SELECT code FROM courses WHERE id = ?", (course_id,)
            ).fetchone()["code"]
        edit_url = f"{detail_url}/announcements/{announcement_id}/edit"
        changed = self.client.post(edit_url, data={
            "title": "新公告", "body": "更新內容", "csrf_token": self.csrf(self.client)
        }, follow_redirects=True)
        self.assertIn("新公告", changed.get_data(as_text=True))
        self.assertNotIn("原內容", changed.get_data(as_text=True))

        student = self.app.test_client()
        self.login(student, "student", "student-pass")
        student.post("/courses/join", data={
            "code": code, "csrf_token": self.csrf(student)
        })
        self.assertEqual(student.get(edit_url).status_code, 403)
        self.assertEqual(student.post(edit_url, data={
            "title": "學生修改", "body": "不允許", "csrf_token": self.csrf(student)
        }).status_code, 403)
        other = self.app.test_client()
        self.login(other, "other-teacher", "other-pass")
        self.assertEqual(other.get(edit_url).status_code, 404)
