import os
import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from config import Config
from database import init_db
from flask_cors import CORS

from routes.dashboard import dashboard_bp
from routes.pages import pages_bp
from routes.residents import residents_bp
from routes.reports import reports_bp
from routes.api import api_bp

BASE_DIR = os.path.dirname(__file__)
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.config.from_object(Config)
app.config.update(
    SECRET_KEY="barangay-shared-secret-key",
    SESSION_COOKIE_NAME="barangay_shared_session",
    SESSION_COOKIE_PATH="/",
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)
app.secret_key = app.config["SECRET_KEY"]

DATABASE = os.path.join(os.path.dirname(__file__), "users.db")
DEFAULT_USERS = {
    "admin": "adminpass",
    "staff": "staffpass",
}


def init_users_db():
    db = sqlite3.connect(DATABASE)
    db.execute(
        """CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )"""
    )
    db.execute("DELETE FROM users")
    for username, password in DEFAULT_USERS.items():
        db.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, generate_password_hash(password, method="pbkdf2:sha256")),
        )
    db.commit()
    db.close()


init_users_db()


@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,Authorization"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,DELETE,OPTIONS"
    return response


@app.before_request
def require_login():
    if request.endpoint == "static" or request.path.startswith("/static/") or request.path in {"/", "/login", "/logout"} or request.path.startswith("/api"):
        return None

    if "username" not in session:
        return redirect(url_for("login"))


@app.route("/", methods=["GET"])
def home():
    if "username" in session:
        return redirect(url_for("dashboard.dashboard"))
    return redirect(url_for("login"))


@app.route("/login", methods=["GET", "POST"], endpoint="login")
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        db = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
        user = db.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
        db.close()

        if user and check_password_hash(user["password"], password):
            session.clear()
            session["username"] = user["username"]
            session["module"] = "resident"
            return redirect(url_for("dashboard.dashboard"))

        return render_template("login.html", error="Invalid username or password")

    if "username" in session:
        return redirect(url_for("dashboard.dashboard"))

    return render_template("login.html", error=None)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


app.register_blueprint(dashboard_bp)
app.register_blueprint(pages_bp)
app.register_blueprint(residents_bp, url_prefix="/api")
app.register_blueprint(reports_bp, url_prefix="/api")
app.register_blueprint(api_bp)


if __name__ == "__main__":
    init_db()
    app.run(
        debug=True,
        host="0.0.0.0",
        port=5000
    )