from flask import Blueprint, jsonify
from database import get_db

reports_bp = Blueprint(
    "reports",
    __name__
)

# =====================================================
# DASHBOARD SUMMARY
# =====================================================

@reports_bp.route(
    "/reports/summary",
    methods=["GET"]
)
def get_summary():

    db = get_db()

    total = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE archived = 0
    """).fetchone()["total"]

    active = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE archived = 0
    """).fetchone()["total"]

    male = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE gender='Male'
        AND archived=0
    """).fetchone()["total"]

    female = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE gender='Female'
        AND archived=0
    """).fetchone()["total"]

    seniors = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE age >= 60
        AND archived=0
    """).fetchone()["total"]

    voters = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE voter_status='Yes'
        AND archived=0
    """).fetchone()["total"]

    archived = db.execute("""
        SELECT COUNT(*) AS total
        FROM residents
        WHERE archived=1
    """).fetchone()["total"]

    recent = db.execute("""
        SELECT *
        FROM residents
        WHERE archived=0
        ORDER BY date_created DESC
        LIMIT 5
    """).fetchall()

    db.close()

    return jsonify({

        "total_residents": total,

        "active_residents": active,

        "archived_residents": archived,

        "male": male,

        "female": female,

        "senior_citizens": seniors,

        "registered_voters": voters,

        "archived": archived,

        "recent_residents":[
            dict(r)
            for r in recent
        ]

    })



# =====================================================
# RESIDENTS BY GENDER
# =====================================================

@reports_bp.route(
    "/reports/gender",
    methods=["GET"]
)
def residents_by_gender():

    db = get_db()

    result = db.execute("""

        SELECT

        gender,

        COUNT(*) AS total

        FROM residents

        WHERE archived=0

        GROUP BY gender

    """).fetchall()

    db.close()

    return jsonify([
        dict(r)
        for r in result
    ])

# =====================================================
# RESIDENTS BY SEX
# =====================================================

@reports_bp.route(
    "/reports/sex",
    methods=["GET"]
)
def residents_by_sex():
    db = get_db()
    result = db.execute("""
        SELECT
            gender AS sex,
            COUNT(*) AS total
        FROM residents
        WHERE archived=0
        GROUP BY gender
    """).fetchall()
    db.close()
    return jsonify([
        dict(r)
        for r in result
    ])

# =====================================================
# AGE DISTRIBUTION
# =====================================================

@reports_bp.route(
    "/reports/age-distribution",
    methods=["GET"]
)
def age_distribution():
    db = get_db()
    categories = [
        ("Child", "0-15" , "age <= 15"),
        ("Youth", "16-30", "age BETWEEN 16 AND 30"),
        ("Adult", "31-59", "age BETWEEN 31 AND 59"),
        ("Seniors", "60+", "age >= 60")
    ]
    result = []
    for name, range_label, condition in categories:
        total = db.execute(f"SELECT COUNT(*) AS total FROM residents WHERE {condition} AND archived=0").fetchone()["total"]
        result.append({
            "category": name,
            "range": range_label,
            "total": total
        })
    db.close()
    return jsonify(result)

# =====================================================
# BLOTTER RESPONDENTS
# =====================================================

@reports_bp.route("/api/reports/blotter-respondents", methods=["GET"])
def blotter_respondents():

    db = get_db()

    try:
        table_exists = db.execute("""
            SELECT name
            FROM sqlite_master
            WHERE type='table' AND name='blotters'
        """).fetchone()

        if table_exists is None:
            return jsonify({
                "success": True,
                "total": 0,
                "respondents": []
            })

        result = db.execute("""
            SELECT
                r.resident_id,
                TRIM(
                    r.first_name || ' ' ||
                    COALESCE(r.middle_name || ' ', '') ||
                    r.last_name
                ) AS name,
                r.gender AS sex,
                r.purok,
                COUNT(b.blotter_id) AS total_complaints
            FROM residents r
            LEFT JOIN blotters b
                ON b.suspect_id = r.resident_id
            WHERE r.archived = 0
            GROUP BY
                r.resident_id,
                r.first_name,
                r.middle_name,
                r.last_name,
                r.gender,
                r.purok
            ORDER BY total_complaints DESC
        """).fetchall()

        return jsonify({
            "success": True,
            "total": len(result),
            "respondents": [dict(row) for row in result]
        })

    finally:
        db.close()

# =====================================================
# RESIDENTS BY PUROK
# =====================================================

@reports_bp.route(
    "/reports/purok",
    methods=["GET"]
)
def residents_by_purok():

    db = get_db()

    result = db.execute("""

        SELECT

        purok,

        COUNT(*) AS total

        FROM residents

        WHERE archived=0

        GROUP BY purok

        ORDER BY purok

    """).fetchall()

    db.close()

    return jsonify([
        dict(r)
        for r in result
    ])

# =====================================================
# CIVIL STATUS REPORT
# =====================================================

@reports_bp.route(
    "/reports/civil-status",
    methods=["GET"]
)
def civil_status_report():

    db = get_db()

    result = db.execute("""

        SELECT

        civil_status,

        COUNT(*) AS total

        FROM residents

        WHERE archived=0

        GROUP BY civil_status

    """).fetchall()

    db.close()

    return jsonify([
        dict(r)
        for r in result
    ])

# ===========================================
# SUMMARY REPORT
# ===========================================
@reports_bp.route("/api/reports/summary", methods=["GET"])
def reports_summary():

    db = get_db()

    total = db.execute("""
        SELECT COUNT(*) AS total
        FROM certificates
    """).fetchone()["total"]

    active = db.execute("""
        SELECT COUNT(*) AS total
        FROM certificates
        WHERE archived = 0
    """).fetchone()["total"]

    archived = db.execute("""
        SELECT COUNT(*) AS total
        FROM certificates
        WHERE archived = 1
    """).fetchone()["total"]

    db.close()

    return jsonify({
        "total_residents": total,
        "active_residents": active,
        "archived_residents": archived
    })


# ===========================================
# CERTIFICATES BY TYPE
# ===========================================
@reports_bp.route("http://127.0.0.1:5001/api/reports/certificate-type", methods=["GET"])
def reports_certificate_type():

    db = get_db()

    rows = db.execute("""
        SELECT
            certificate_type AS purok,
            COUNT(*) AS total
        FROM certificates
        GROUP BY certificate_type
        ORDER BY total DESC
    """).fetchall()

    db.close()

    return jsonify([dict(row) for row in rows])
