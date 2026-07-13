from flask import Blueprint, render_template
from database import query_db

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/reports")
def reports():
    return render_template("reports.html")


@pages_bp.route("/archive")
def archive():
    return render_template("archive.html")


@pages_bp.route("/residents")
def residents():
    return render_template("residents.html")


@pages_bp.route("/residents/<int:resident_id>")
def resident_view(resident_id):
    return render_template("resident_view.html", resident_id=resident_id)


@pages_bp.route("/residents/<int:resident_id>/edit")
def edit_resident(resident_id):
    return render_template("resident_edit.html", resident_id=resident_id)


@pages_bp.route("/residents/new")
def resident_form():
    return render_template("resident_form.html")


@pages_bp.route("/dashboards")
def dashboard():
    return render_template("index.html")