"""Messages for members of a course."""

from flask import Blueprint, abort, flash, g, redirect, request, url_for

from app.models import accessible_course, get_db
from app.routes.auth import login_required

bp = Blueprint("messages", __name__)


@bp.post("/courses/<int:course_id>/messages")
@login_required
def create(course_id):
    if accessible_course(course_id, g.user) is None:
        abort(404)
    body = request.form.get("body", "").strip()
    if not body:
        flash("留言不可空白。", "danger")
    else:
        get_db().execute(
            "INSERT INTO messages (course_id, author_id, body) VALUES (?, ?, ?)",
            (course_id, g.user["id"], body),
        )
        get_db().commit()
    return redirect(url_for("courses.detail", course_id=course_id))
