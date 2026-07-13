from flask import Blueprint, render_template
from database import query_db

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/dashboard")
def dashboard():

    residents = query_db(
        "SELECT COUNT(*) AS total FROM residents WHERE archived = 0 AND status = 'Active'",
        one=True
    )["total"]

    certificates = 0
    blotters = 0

    return render_template(
        "index.html",
        residents=residents,
        certificates=certificates,
        blotters=blotters
    )