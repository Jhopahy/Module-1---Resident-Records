import json
from flask import Blueprint, jsonify
from database import get_db

api_bp = Blueprint("api", __name__)


@api_bp.route("/api/status")
def status():

    return jsonify({
        "status": "online",
        "module": "Residence Records"
    })

#===============================
# Export Resident Data to JSON
#===============================
@api_bp.route("/api/residents/<int:resident_id>", methods=["GET"])
def get_resident(resident_id):

    db = get_db()

    resident = db.execute(
        """
        SELECT
            resident_id,
            first_name,
            middle_name,
            last_name,
            suffix
        FROM residents
        WHERE resident_id = ?
        """,
        (resident_id,)
    ).fetchone()

    db.close()

    if resident is None:
        return jsonify({
            "success": False,
            "message": "Resident not found"
        }), 404

    resident = dict(resident)

    full_name = f"{resident['first_name']}"

    if resident["middle_name"]:
        full_name += f" {resident['middle_name']}"

    full_name += f" {resident['last_name']}"

    if resident["suffix"]:
        full_name += f" {resident['suffix']}"

    return jsonify({
        "success": True,
        "resident": {
            "resident_id": resident["resident_id"],
            "resident_name": full_name
        }
    })

# FETCH CERTIFICATE DATA
@api_bp.route("/api/certificates/total", methods=["GET"])
def total_certificates():

    db = get_db()

    total = db.execute(
        """
        SELECT COUNT(*) AS total
        FROM certificates
        """
    ).fetchone()

    db.close()

    return jsonify({
        "success": True,
        "total_certificates": total["total"]
    })

# EXPORT TOTAL RESIDENTS COUNT
@api_bp.route("/api/residents/count", methods=["GET"])
def total_residents():

    db = get_db()

    total = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE archived = 0
    """).fetchone()

    db.close()

    return jsonify({
        "total": total["total"]
    })


@api_bp.route("/api/blotters/count", methods=["GET"])
def total_blotters():

    db = get_db()

    try:
        table_exists = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='blotters'"
        ).fetchone()

        if table_exists is None:
            return jsonify({
                "success": True,
                "total": 0
            })

        result = db.execute("""
            SELECT COUNT(*) AS total
            FROM blotters
        """).fetchone()

        return jsonify({
            "success": True,
            "total": result["total"] if result else 0
        })
    finally:
        db.close()