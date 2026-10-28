"""Teacher assignments within an owned course and student file submissions."""

from flask import (
    Blueprint, abort, current_app, flash, g, redirect, render_template, request,
    send_from_directory, url_for,
)

from app.models import (
    accessible_course, course_assignment, create_assignment, own_submission, past_due,
    submit_assignment,
)
from app.routes.auth import login_required, teacher_required

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


def member_assignment(course_id, assignment_id):
    course = accessible_course(course_id, g.user)
    assignment = course_assignment(course_id, assignment_id) if course else None
    if assignment is None:
        abort(404)
    return course, assignment


@bp.get("/courses/<int:course_id>/assignments/<int:assignment_id>")
@login_required
def detail(course_id, assignment_id):
    course, assignment = member_assignment(course_id, assignment_id)
    submission = (
        own_submission(assignment_id, g.user["id"]) if g.user["role"] == "student" else None
    )
    return render_template(
        "assignment_detail.html",
        course=course,
        assignment=assignment,
        submission=submission,
        closed=past_due(assignment),
        allowed_extensions=current_app.config["ALLOWED_EXTENSIONS"],
        max_upload_kb=current_app.config["MAX_UPLOAD_BYTES"] // 1024,
    )


@bp.post("/courses/<int:course_id>/assignments/<int:assignment_id>/submission")
@login_required
def submit(course_id, assignment_id):
    _course, assignment = member_assignment(course_id, assignment_id)
    if g.user["role"] != "student":
        abort(403)
    try:
        submit_assignment(assignment, g.user["id"], request.files.get("file"))
        flash("已繳交", "success")
    except ValueError as exc:
        flash(str(exc), "danger")
    return redirect(url_for("assignments.detail", course_id=course_id, assignment_id=assignment_id))


@bp.get("/courses/<int:course_id>/assignments/<int:assignment_id>/submission")
@login_required
def download(course_id, assignment_id):
    member_assignment(course_id, assignment_id)
    if g.user["role"] != "student":
        abort(403)
    submission = own_submission(assignment_id, g.user["id"])
    if submission is None:
        abort(404)
    return send_from_directory(
        current_app.config["UPLOAD_FOLDER"],
        submission["stored_name"],
        as_attachment=True,
        download_name=submission["original_name"],
    )
