"""End-to-end checks for the agreed Mini Moodle user stories."""

import io
import re
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app import create_app
from app.models import TAIPEI, create_assignment, create_user, get_db, past_due


class AppStoryTests(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.app = create_app({
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "DATABASE": str(Path(self.tempdir.name) / "test.sqlite3"),
            "UPLOAD_FOLDER": str(Path(self.tempdir.name) / "uploads"),
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
        self.assertIn('<h1 id="welcome-title">Mini Moodle</h1>', html)
        self.assertNotIn("迷你教學平台", html)
        self.assertNotIn("・", html)
        self.assertNotIn("。", html)
        css = self.client.get("/static/css/style.css")
        self.assertEqual(css.status_code, 200)
        self.assertIn(".welcome-panel", css.get_data(as_text=True))
        css.close()

    def test_sqlite_utc_timestamp_displays_as_taiwan_time(self):
        formatter = self.app.jinja_env.filters["taipei_time"]
        self.assertEqual(
            formatter("2026-10-25 16:38:45"), "2026-10-26 00:38（台灣時間）"
        )

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

    def assignment_count(self):
        with self.app.app_context():
            return get_db().execute("SELECT count(*) FROM assignments").fetchone()[0]

    def test_teacher_creates_assignment_and_student_sees_it(self):
        course_id = self.create_course()
        detail_url = f"/courses/{course_id}"
        with self.app.app_context():
            code = get_db().execute(
                "SELECT code FROM courses WHERE id = ?", (course_id,)
            ).fetchone()["code"]
        due = datetime.now(TAIPEI) + timedelta(days=7)
        created = self.client.post(f"{detail_url}/assignments", data={
            "title": "期中報告", "description": "繳交需求文件",
            "due_at": due.strftime("%Y-%m-%dT%H:%M"), "csrf_token": self.csrf(self.client)
        }, follow_redirects=True)
        html = created.get_data(as_text=True)
        self.assertIn("期中報告", html)
        self.assertIn("繳交需求文件", html)
        self.assertIn(due.strftime("%Y-%m-%d %H:%M") + "（台灣時間）", html)
        self.assertEqual(self.assignment_count(), 1)

        student = self.app.test_client()
        self.login(student, "student", "student-pass")
        student.post("/courses/join", data={"code": code, "csrf_token": self.csrf(student)})
        student_html = student.get(detail_url).get_data(as_text=True)
        self.assertIn("期中報告", student_html)
        self.assertNotIn("建立作業</button>", student_html)
        self.assertEqual(student.post(f"{detail_url}/assignments", data={
            "title": "學生作業", "due_at": due.strftime("%Y-%m-%dT%H:%M"),
            "csrf_token": self.csrf(student)
        }).status_code, 403)

        other = self.app.test_client()
        self.login(other, "other-teacher", "other-pass")
        self.assertEqual(other.post(f"{detail_url}/assignments", data={
            "title": "偽作業", "due_at": due.strftime("%Y-%m-%dT%H:%M"),
            "csrf_token": self.csrf(other)
        }).status_code, 404)
        self.assertEqual(self.assignment_count(), 1)

    def test_assignment_requires_title_and_future_deadline(self):
        course_id = self.create_course()
        url = f"/courses/{course_id}/assignments"
        future = (datetime.now(TAIPEI) + timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
        past = (datetime.now(TAIPEI) - timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M")
        cases = [
            ({"title": "  ", "due_at": future}, "作業標題與截止時間不可空白"),
            ({"title": "期中報告", "due_at": ""}, "作業標題與截止時間不可空白"),
            ({"title": "期中報告", "due_at": "明天"}, "截止時間格式不正確"),
            ({"title": "期中報告", "due_at": past}, "截止時間不可早於現在"),
        ]
        for data, message in cases:
            response = self.client.post(url, data={
                **data, "csrf_token": self.csrf(self.client)
            }, follow_redirects=True)
            self.assertIn(message, response.get_data(as_text=True))
        self.assertEqual(self.assignment_count(), 0)

        now = datetime(2026, 11, 5, 15, 59, tzinfo=timezone.utc)
        with self.app.app_context():
            assignment_id = create_assignment(course_id, "邊界", "", "2026-11-05T23:59", now=now)
            due_at = get_db().execute(
                "SELECT due_at FROM assignments WHERE id = ?", (assignment_id,)
            ).fetchone()["due_at"]
            self.assertEqual(due_at, "2026-11-05 15:59:00")
            with self.assertRaisesRegex(ValueError, "截止時間不可早於現在"):
                create_assignment(course_id, "太晚", "", "2026-11-05T23:58", now=now)

    def enrolled_assignment(self, due_at):
        course_id = self.create_course()
        with self.app.app_context():
            db = get_db()
            code = db.execute("SELECT code FROM courses WHERE id = ?", (course_id,)).fetchone()["code"]
            assignment_id = db.execute(
                "INSERT INTO assignments (course_id, title, due_at) VALUES (?, ?, ?)",
                (course_id, "期中報告", due_at.strftime("%Y-%m-%d %H:%M:%S")),
            ).lastrowid
            db.commit()
        student = self.app.test_client()
        self.login(student, "student", "student-pass")
        student.post("/courses/join", data={"code": code, "csrf_token": self.csrf(student)})
        return course_id, assignment_id, code, student

    def upload(self, client, url, content, filename):
        return client.post(f"{url}/submission", data={
            "file": (io.BytesIO(content), filename), "csrf_token": self.csrf(client)
        }, content_type="multipart/form-data", follow_redirects=True)

    def submission_rows(self):
        with self.app.app_context():
            return get_db().execute("SELECT * FROM submissions").fetchall()

    def uploaded_files(self):
        return list(Path(self.app.config["UPLOAD_FOLDER"]).iterdir())

    def test_student_submits_and_resubmits_before_deadline(self):
        course_id, assignment_id, _code, student = self.enrolled_assignment(
            datetime.now(timezone.utc) + timedelta(days=1)
        )
        url = f"/courses/{course_id}/assignments/{assignment_id}"
        self.assertIn("未繳交", student.get(f"/courses/{course_id}").get_data(as_text=True))
        self.assertIn("未繳交", student.get(url).get_data(as_text=True))

        html = self.upload(student, url, b"first", "report.pdf").get_data(as_text=True)
        self.assertIn("已繳交", html)
        self.assertIn("report.pdf", html)
        self.assertIn("繳交時間", html)
        self.assertIn("重新繳交</button>", html)
        self.assertIn("已繳交", student.get(f"/courses/{course_id}").get_data(as_text=True))

        self.upload(student, url, b"second", "第二版.txt")
        rows = self.submission_rows()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["original_name"], "第二版.txt")
        self.assertEqual(len(self.uploaded_files()), 1)
        download = student.get(f"{url}/submission")
        self.assertEqual(download.data, b"second")
        self.assertIn("attachment", download.headers["Content-Disposition"])
        download.close()

        self.assertNotIn("繳交</button>", self.client.get(url).get_data(as_text=True))
        self.assertEqual(self.client.post(f"{url}/submission", data={
            "csrf_token": self.csrf(self.client)
        }).status_code, 403)

    def test_invalid_or_late_submission_creates_nothing(self):
        course_id, assignment_id, _code, student = self.enrolled_assignment(
            datetime.now(timezone.utc) + timedelta(days=1)
        )
        url = f"/courses/{course_id}/assignments/{assignment_id}"
        cases = [
            (b"x", "virus.exe", "只接受 pdf、docx、zip、txt 檔案"),
            (b"x", "", "請選擇要繳交的檔案"),
            (b"x" * (120 * 1024), "big.pdf", "檔案超過 100 KB"),
            (b"x" * (300 * 1024), "huge.pdf", "檔案超過 100 KB"),
        ]
        for content, filename, message in cases:
            self.assertIn(message, self.upload(student, url, content, filename).get_data(as_text=True))
        self.assertEqual(self.submission_rows(), [])
        self.assertEqual(self.uploaded_files(), [])

        with self.app.app_context():
            db = get_db()
            db.execute("UPDATE assignments SET due_at = ? WHERE id = ?", (
                (datetime.now(timezone.utc) - timedelta(minutes=1)).strftime("%Y-%m-%d %H:%M:%S"),
                assignment_id,
            ))
            db.commit()
            assignment = db.execute("SELECT * FROM assignments WHERE id = ?", (assignment_id,)).fetchone()
        closed_html = student.get(url).get_data(as_text=True)
        self.assertIn("已截止", closed_html)
        self.assertNotIn("繳交</button>", closed_html)
        self.assertIn("已截止", student.get(f"/courses/{course_id}").get_data(as_text=True))
        self.assertIn("已截止", self.upload(student, url, b"late", "late.pdf").get_data(as_text=True))
        self.assertEqual(self.submission_rows(), [])
        self.assertEqual(self.uploaded_files(), [])

        due = datetime.strptime(assignment["due_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        self.assertFalse(past_due(assignment, now=due))
        self.assertTrue(past_due(assignment, now=due + timedelta(seconds=1)))

    def test_submissions_are_private_to_enrolled_owner(self):
        course_id, assignment_id, code, student = self.enrolled_assignment(
            datetime.now(timezone.utc) + timedelta(days=1)
        )
        url = f"/courses/{course_id}/assignments/{assignment_id}"
        self.upload(student, url, b"mine", "my-report.pdf")

        outsider = self.app.test_client()
        self.login(outsider, "outsider", "outsider-pass")
        self.assertEqual(outsider.get(url).status_code, 404)
        self.assertEqual(outsider.get(f"{url}/submission").status_code, 404)
        self.assertEqual(outsider.post(f"{url}/submission", data={
            "file": (io.BytesIO(b"x"), "x.pdf"), "csrf_token": self.csrf(outsider)
        }, content_type="multipart/form-data").status_code, 404)

        with self.app.app_context():
            create_user("classmate", "classmate-pass", "student")
        classmate = self.app.test_client()
        self.login(classmate, "classmate", "classmate-pass")
        classmate.post("/courses/join", data={"code": code, "csrf_token": self.csrf(classmate)})
        classmate_html = classmate.get(url).get_data(as_text=True)
        self.assertNotIn("my-report.pdf", classmate_html)
        self.assertIn("未繳交", classmate_html)
        self.assertEqual(classmate.get(f"{url}/submission").status_code, 404)
        self.assertEqual(len(self.submission_rows()), 1)
