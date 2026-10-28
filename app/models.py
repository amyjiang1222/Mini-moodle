"""Small SQLite data layer for the agreed Jira stories."""

import os
import secrets
import sqlite3
import string
import uuid
from datetime import datetime, timedelta, timezone

from flask import current_app, g
from werkzeug.security import generate_password_hash

TAIPEI = timezone(timedelta(hours=8))

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('teacher', 'student'))
);
CREATE TABLE IF NOT EXISTS courses (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL CHECK (length(trim(name)) > 0),
    description TEXT NOT NULL DEFAULT '',
    code TEXT NOT NULL UNIQUE,
    teacher_id INTEGER NOT NULL REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS enrollments (
    student_id INTEGER NOT NULL REFERENCES users(id),
    course_id INTEGER NOT NULL REFERENCES courses(id),
    PRIMARY KEY (student_id, course_id)
);
CREATE TABLE IF NOT EXISTS announcements (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    teacher_id INTEGER NOT NULL REFERENCES users(id),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    body TEXT NOT NULL CHECK (length(trim(body)) > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    author_id INTEGER NOT NULL REFERENCES users(id),
    body TEXT NOT NULL CHECK (length(trim(body)) > 0),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS assignments (
    id INTEGER PRIMARY KEY,
    course_id INTEGER NOT NULL REFERENCES courses(id),
    title TEXT NOT NULL CHECK (length(trim(title)) > 0),
    description TEXT NOT NULL DEFAULT '',
    due_at TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY,
    assignment_id INTEGER NOT NULL REFERENCES assignments(id),
    student_id INTEGER NOT NULL REFERENCES users(id),
    original_name TEXT NOT NULL,
    stored_name TEXT NOT NULL,
    submitted_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (assignment_id, student_id)
);
"""


def get_db():
    if "db" not in g:
        db = sqlite3.connect(current_app.config["DATABASE"])
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys = ON")
        g.db = db
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    get_db().executescript(SCHEMA)
    get_db().commit()


def create_user(username, password, role):
    if role not in {"teacher", "student"}:
        raise ValueError("角色必須是 teacher 或 student")
    username = username.strip()
    if not username or not password:
        raise ValueError("帳號與密碼不可空白")
    db = get_db()
    cursor = db.execute(
        "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
        (username, generate_password_hash(password), role),
    )
    db.commit()
    return cursor.lastrowid


def new_course_code():
    letters = string.ascii_uppercase
    digits = string.digits
    return "".join(secrets.choice(letters) for _ in range(2)) + "".join(
        secrets.choice(digits) for _ in range(7)
    )


def create_course(name, description, teacher_id):
    name = name.strip()
    if not name:
        raise ValueError("課程名稱不可空白")
    db = get_db()
    for _ in range(12):
        try:
            cursor = db.execute(
                "INSERT INTO courses (name, description, code, teacher_id) VALUES (?, ?, ?, ?)",
                (name, description.strip(), new_course_code(), teacher_id),
            )
            db.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError as exc:
            if "courses.code" not in str(exc):
                raise
    raise RuntimeError("無法產生不重複的課碼")


def create_assignment(course_id, title, description, due_input, now=None):
    """Store the deadline in UTC; the form's datetime-local value is Taiwan time."""
    title = title.strip()
    if not title or not due_input:
        raise ValueError("作業標題與截止時間不可空白")
    try:
        due_local = datetime.strptime(due_input, "%Y-%m-%dT%H:%M").replace(tzinfo=TAIPEI)
    except ValueError:
        raise ValueError("截止時間格式不正確") from None
    due_utc = due_local.astimezone(timezone.utc)
    if due_utc < (now or datetime.now(timezone.utc)):
        raise ValueError("截止時間不可早於現在")
    db = get_db()
    cursor = db.execute(
        "INSERT INTO assignments (course_id, title, description, due_at) VALUES (?, ?, ?, ?)",
        (course_id, title, description.strip(), due_utc.strftime("%Y-%m-%d %H:%M:%S")),
    )
    db.commit()
    return cursor.lastrowid


def course_assignment(course_id, assignment_id):
    return get_db().execute(
        "SELECT * FROM assignments WHERE id = ? AND course_id = ?", (assignment_id, course_id)
    ).fetchone()


def past_due(assignment, now=None):
    due = datetime.strptime(assignment["due_at"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
    return (now or datetime.now(timezone.utc)) > due


def own_submission(assignment_id, student_id):
    return get_db().execute(
        "SELECT * FROM submissions WHERE assignment_id = ? AND student_id = ?",
        (assignment_id, student_id),
    ).fetchone()


def upload_limit_message():
    return f"檔案超過 {current_app.config['MAX_UPLOAD_BYTES'] // 1024} KB"


def submit_assignment(assignment, student_id, upload, now=None):
    """Validate before writing anything; a resubmission replaces the student's only record."""
    if past_due(assignment, now):
        raise ValueError("已截止")
    original_name = (upload.filename or "").replace("\\", "/").rsplit("/", 1)[-1].strip() if upload else ""
    if not original_name:
        raise ValueError("請選擇要繳交的檔案")
    extension = original_name.rsplit(".", 1)[-1].lower() if "." in original_name else ""
    allowed = current_app.config["ALLOWED_EXTENSIONS"]
    if extension not in allowed:
        raise ValueError("只接受 " + "、".join(allowed) + " 檔案")
    upload.stream.seek(0, os.SEEK_END)
    size = upload.stream.tell()
    upload.stream.seek(0)
    if size > current_app.config["MAX_UPLOAD_BYTES"]:
        raise ValueError(upload_limit_message())

    folder = current_app.config["UPLOAD_FOLDER"]
    stored_name = f"{uuid.uuid4().hex}.{extension}"
    upload.save(os.path.join(folder, stored_name))
    previous = own_submission(assignment["id"], student_id)
    db = get_db()
    try:
        db.execute(
            "INSERT INTO submissions (assignment_id, student_id, original_name, stored_name) "
            "VALUES (?, ?, ?, ?) ON CONFLICT (assignment_id, student_id) DO UPDATE SET "
            "original_name = excluded.original_name, stored_name = excluded.stored_name, "
            "submitted_at = CURRENT_TIMESTAMP",
            (assignment["id"], student_id, original_name, stored_name),
        )
        db.commit()
    except Exception:
        os.remove(os.path.join(folder, stored_name))
        raise
    if previous is not None:
        try:
            os.remove(os.path.join(folder, previous["stored_name"]))
        except FileNotFoundError:
            pass


def visible_courses(user):
    db = get_db()
    if user["role"] == "teacher":
        return db.execute(
            "SELECT * FROM courses WHERE teacher_id = ? ORDER BY id DESC", (user["id"],)
        ).fetchall()
    return db.execute(
        "SELECT c.* FROM courses c JOIN enrollments e ON e.course_id = c.id "
        "WHERE e.student_id = ? ORDER BY c.id DESC",
        (user["id"],),
    ).fetchall()


def accessible_course(course_id, user):
    db = get_db()
    if user["role"] == "teacher":
        return db.execute(
            "SELECT * FROM courses WHERE id = ? AND teacher_id = ?",
            (course_id, user["id"]),
        ).fetchone()
    return db.execute(
        "SELECT c.* FROM courses c JOIN enrollments e ON e.course_id = c.id "
        "WHERE c.id = ? AND e.student_id = ?",
        (course_id, user["id"]),
    ).fetchone()
