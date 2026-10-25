"""Teacher announcements within an owned course."""

from flask import Blueprint, abort, flash, g, redirect, render_template, request, url_for

from app.models import accessible_course, get_db
from app.routes.auth import teacher_required

bp = Blueprint("announcements", __name__)


@bp.post("/courses/<int:course_id>/announcements")
@teacher_required
def create(course_id):
    if accessible_course(course_id, g.user) is None:
        abort(404)
    title = request.form.get("title", "").strip()
    body = request.form.get("body", "").strip()
    if not title or not body:
        flash("公告標題與內容不可空白。", "danger")
    else:
        get_db().execute(
            "INSERT INTO announcements (course_id, teacher_id, title, body) VALUES (?, ?, ?, ?)",
            (course_id, g.user["id"], title, body),
        )
        get_db().commit()
    return redirect(url_for("courses.detail", course_id=course_id))


@bp.route("/courses/<int:course_id>/announcements/<int:announcement_id>/edit", methods=["GET", "POST"])
@teacher_required
def edit(course_id, announcement_id):
    course = accessible_course(course_id, g.user)
    if course is None:
        abort(404)
    db = get_db()
    announcement = db.execute(
        "SELECT * FROM announcements WHERE id = ? AND course_id = ? AND teacher_id = ?",
        (announcement_id, course_id, g.user["id"]),
    ).fetchone()
    if announcement is None:
        abort(404)
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        body = request.form.get("body", "").strip()
        if not title or not body:
            flash("公告標題與內容不可空白。", "danger")
        else:
            db.execute(
                "UPDATE announcements SET title = ?, body = ? WHERE id = ?",
                (title, body, announcement_id),
            )
            db.commit()
            flash("公告已更新。", "success")
            return redirect(url_for("courses.detail", course_id=course_id))
    return render_template("announcement_edit.html", course=course, announcement=announcement)
