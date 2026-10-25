"""Small SQLite data layer for the five agreed Jira stories."""

import secrets
import sqlite3
import string

from flask import current_app, g
from werkzeug.security import generate_password_hash


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
