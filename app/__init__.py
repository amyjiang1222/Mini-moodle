"""Mini Moodle 應用程式工廠。"""

from flask import Flask, render_template

from config import Config


def create_app(test_config=None):
    """建立 Flask 應用程式，測試時可傳入設定覆寫值。"""
    app = Flask(__name__)
    app.config.from_object(Config)
    if test_config is not None:
        app.config.update(test_config)

    @app.get("/")
    def dashboard():
        return render_template("dashboard.html")

    return app
