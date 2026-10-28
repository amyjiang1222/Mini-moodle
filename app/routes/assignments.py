"""Teacher assignments within an owned course."""

from flask import Blueprint, abort, flash, g, redirect, request, url_for

from app.models import accessible_course, create_assignment
from app.routes.auth import teacher_required

bp = Blueprint("assignments", __name__)


@bp.post("/courses/<int:course_id>/assignments")
@teacher_required
def create(course_id):
    if accessible_course(course_id, g.user) is None:
        abort(404)
    try:
        create_assignment(
            course_id,
            request.form.get("title", ""),
            request.form.get("description", ""),
            request.form.get("due_at", ""),
        )
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("courses.detail", course_id=course_id))
