"""Course creation, student enrollment, and course access."""

import sqlite3

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.models import accessible_course, create_course, get_db
from app.routes.auth import login_required, teacher_required

bp = Blueprint("courses", __name__)


@bp.route("/courses/new", methods=["GET", "POST"])
@teacher_required
def new():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        if not name:
            flash("課程名稱不可空白", "danger")
        else:
            course_id = create_course(name, description, g.user["id"])
            return redirect(url_for("courses.detail", course_id=course_id))
    return render_template("course_new.html")


@bp.post("/courses/join")
@login_required
def join():
    if g.user["role"] != "student":
        abort(403)
    code = request.form.get("code", "").strip().upper()
    course = get_db().execute("SELECT id FROM courses WHERE code = ?", (code,)).fetchone()
    if course is None:
        flash("找不到這個課碼", "danger")
        return redirect(url_for("dashboard"))
    try:
        get_db().execute(
            "INSERT INTO enrollments (student_id, course_id) VALUES (?, ?)",
            (g.user["id"], course["id"]),
        )
        get_db().commit()
    except sqlite3.IntegrityError:
        flash("你已加入這門課程", "info")
    return redirect(url_for("courses.detail", course_id=course["id"]))


@bp.get("/courses/<int:course_id>")
@login_required
def detail(course_id):
    course = accessible_course(course_id, g.user)
    if course is None:
        abort(404)
    db = get_db()
    announcements = db.execute(
        "SELECT a.*, u.username AS author FROM announcements a "
        "JOIN users u ON u.id = a.teacher_id WHERE a.course_id = ? ORDER BY a.id DESC",
        (course_id,),
    ).fetchall()
    assignments = db.execute(
        "SELECT a.*, s.submitted_at, a.due_at < datetime('now') AS closed FROM assignments a "
        "LEFT JOIN submissions s ON s.assignment_id = a.id AND s.student_id = ? "
        "WHERE a.course_id = ? ORDER BY a.due_at, a.id",
        (g.user["id"], course_id),
    ).fetchall()
    messages = db.execute(
        "SELECT m.*, u.username AS author FROM messages m "
        "JOIN users u ON u.id = m.author_id WHERE m.course_id = ? ORDER BY m.id DESC",
        (course_id,),
    ).fetchall()
    return render_template(
        "course_detail.html",
        course=course,
        announcements=announcements,
        assignments=assignments,
        messages=messages,
    )
