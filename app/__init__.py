"""Mini Moodle application factory."""

import os
import secrets
from datetime import datetime, timezone

from flask import Flask, abort, g, redirect, render_template, request, session, url_for

from app.models import TAIPEI
from config import Config


def create_app(test_config=None):
    """Build the classroom demo app; tests can override all configuration."""
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)
    app.config.update(
        DATABASE=os.path.join(app.instance_path, "mini_moodle.sqlite3"),
        SECRET_KEY=os.environ.get("MINI_MOODLE_SECRET_KEY") or secrets.token_hex(32),
    )
    if test_config is not None:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    @app.template_filter("taipei_time")
    def taipei_time(value):
        """Display SQLite's UTC timestamp in the course's local time zone."""
        utc_time = datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        local_time = utc_time.astimezone(TAIPEI)
        return local_time.strftime("%Y-%m-%d %H:%M") + "（台灣時間）"

    from app.models import close_db, get_db, init_db, visible_courses
    app.teardown_appcontext(close_db)

    with app.app_context():
        init_db()

    @app.before_request
    def load_user_and_check_csrf():
        user_id = session.get("user_id")
        g.user = (
            get_db().execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
            if user_id is not None
            else None
        )
        if request.method == "POST" and not secrets.compare_digest(
            str(session.get("csrf_token", "")), str(request.form.get("csrf_token", "!"))
        ):
            abort(400)

    @app.context_processor
    def inject_csrf_token():
        if "csrf_token" not in session:
            session["csrf_token"] = secrets.token_hex(32)
        return {"csrf_token": session["csrf_token"]}

    @app.get("/")
    def dashboard():
        if g.user is None:
            return render_template("dashboard.html", courses=[])
        return render_template("dashboard.html", courses=visible_courses(g.user))

    from app.routes.auth import bp as auth_bp
    from app.routes.courses import bp as courses_bp
    from app.routes.announcements import bp as announcements_bp
    from app.routes.messages import bp as messages_bp
    from app.routes.assignments import bp as assignments_bp
    app.register_blueprint(auth_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(announcements_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(assignments_bp)

    @app.cli.command("create-user")
    def create_user_command():
        """Create a demo account interactively, without storing a default password."""
        import click
        from app.models import create_user

        username = click.prompt("帳號")
        role = click.prompt("角色", type=click.Choice(["teacher", "student"]))
        password = click.prompt("密碼", hide_input=True, confirmation_prompt=True)
        create_user(username, password, role)
        click.echo("帳號已建立")

    return app
