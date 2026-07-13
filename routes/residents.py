from datetime import datetime, timedelta

from flask import Blueprint, jsonify, request
from database import get_db

residents_bp = Blueprint("residents", __name__)


def calculate_age(birth_date):
    if not birth_date:
        return None

    try:
        dob = datetime.strptime(birth_date, "%Y-%m-%d").date()
    except ValueError:
        return None

    today = datetime.now().date()
    age = today.year - dob.year

    if (today.month, today.day) < (dob.month, dob.day):
        age -= 1

    return age


def calculate_period_of_residence(years_of_residency):
    if years_of_residency is None:
        return None

    try:
        years = int(float(years_of_residency))
        months = int(round((float(years_of_residency) - years) * 12))
    except (TypeError, ValueError):
        return None

    if months < 0 or years < 0:
        return None

    if months == 12:
        years += 1
        months = 0

    parts = []
    if years > 0:
        parts.append(f"{years} yr{'s' if years != 1 else ''}")
    if months > 0:
        parts.append(f"{months} mo{'s' if months != 1 else ''}")

    return " ".join(parts) if parts else "0 mos"


def enhance_resident(resident):
    resident = dict(resident)
    resident["sex"] = resident.get("gender")
    resident["period_of_residence"] = calculate_period_of_residence(
        resident.get("years_of_residency")
    )
    return resident


# =====================================================
# GET ALL RESIDENTS
# =====================================================

@residents_bp.route(
    "/residents",
    methods=["GET"]
)
def get_residents():

    db = get_db()

    residents = db.execute(
        """
        SELECT *
        FROM residents
        WHERE archived = 0
        AND status = 'Active'
        ORDER BY date_created DESC
        """
    ).fetchall()

    db.close()

    return jsonify([
        enhance_resident(r)
        for r in residents
    ])




# =====================================================
# GET SINGLE RESIDENT
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>",
    methods=["GET"]
)
def get_resident(resident_id):

    db = get_db()

    resident = db.execute(
        """
        SELECT *
        FROM residents
        WHERE resident_id = ?
        AND archived = 0
        """,
        (resident_id,)
    ).fetchone()

    db.close()

    if resident is None:
        return jsonify({
            "error":"Resident not found"
        }),404

    return jsonify(enhance_resident(resident))



# =====================================================
# ADD RESIDENT
# =====================================================

@residents_bp.route(
    "/residents",
    methods=["POST"]
)
def add_resident():

    data = request.json or {}

    birth_date = data.get("birth_date")
    calculated_age = calculate_age(birth_date)
    if calculated_age is None and data.get("age"):
        calculated_age = data.get("age")

    required_fields = [
        "first_name",
        "last_name",
        "birth_date",
        "gender",
        "civil_status",
        "house_number",
        "purok",
        "contact_number",
        "years_of_residence",
        "months_of_residence"
    ]

    for field in required_fields:
        if not data.get(field) and data.get(field) != 0:
            field_name = field.replace('_', ' ').title()
            return jsonify({
                "error": f"{field_name} is required"
            }), 400

    if calculated_age is None:
        return jsonify({
            "error": "Age is required when birth date is not provided"
        }), 400

    try:
        purok = int(data.get("purok"))
        if purok < 1 or purok > 5:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({
            "error": "Purok must be an integer between 1 and 5"
        }), 400

    try:
        years = int(data.get("years_of_residence", 0))
        months = int(data.get("months_of_residence", 0))
        if years < 0 or months < 0 or months > 11:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({
            "error": "Years and months of residence must be non-negative and months must be between 0 and 11"
        }), 400

    years_of_residency = years + (months / 12)

    religion = data.get("religion")
    if religion == "Others":
        religion = data.get("religion_other") or "Others"

    db = get_db()

    cursor = db.execute(
        """
        INSERT INTO residents
        (
            first_name,
            middle_name,
            last_name,
            suffix,
            birth_date,
            age,
            gender,
            civil_status,
            nationality,
            religion,
            occupation,
            house_number,
            purok,
            contact_number,
            email,
            years_of_residency,
            voter_status,
            status,
            archived_reason
        )
        VALUES
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,
        (
            data["first_name"],
            data.get("middle_name"),
            data["last_name"],
            data.get("suffix"),
            birth_date,
            calculated_age,
            data["gender"],
            data["civil_status"],
            data.get("nationality", "Filipino"),
            religion,
            data.get("occupation"),
            data["house_number"],
            purok,
            data["contact_number"],
            data.get("email"),
            years_of_residency,
            data.get("voter_status", "No"),
            "Active",
            None
        )
    )

    db.commit()

    resident_id = cursor.lastrowid

    resident = db.execute(
        """
        SELECT *
        FROM residents
        WHERE resident_id=?
        """,
        (resident_id,)
    ).fetchone()

    db.close()

    return jsonify(dict(resident)),201



# =====================================================
# UPDATE RESIDENT
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>",
    methods=["PUT"]
)
def update_resident(resident_id):

    data=request.json or {}

    birth_date = data.get("birth_date")
    calculated_age = calculate_age(birth_date)
    if calculated_age is None and data.get("age"):
        calculated_age = data.get("age")

    try:
        purok = int(data.get("purok"))
        if purok < 1 or purok > 5:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({
            "error": "Purok must be an integer between 1 and 5"
        }), 400

    try:
        years = int(data.get("years_of_residence", 0))
        months = int(data.get("months_of_residence", 0))
        if years < 0 or months < 0 or months > 11:
            raise ValueError()
    except (TypeError, ValueError):
        return jsonify({
            "error": "Years and months of residence must be non-negative and months must be between 0 and 11"
        }), 400

    years_of_residency = years + (months / 12)

    religion = data.get("religion")
    if religion == "Others":
        religion = data.get("religion_other") or "Others"

    db = get_db()

    db.execute(
        """
        UPDATE residents
        SET
            first_name=?,
            middle_name=?,
            last_name=?,
            suffix=?,
            birth_date=?,
            age=?,
            gender=?,
            civil_status=?,
            nationality=?,
            religion=?,
            occupation=?,
            house_number=?,
            purok=?,
            contact_number=?,
            email=?,
            years_of_residency=?,
            voter_status=?,
            status='Active',
            date_updated=datetime('now')
        WHERE resident_id=?
        """,
        (
            data["first_name"],
            data.get("middle_name"),
            data["last_name"],
            data.get("suffix"),
            birth_date,
            calculated_age,
            data["gender"],
            data["civil_status"],
            data.get("nationality"),
            religion,
            data.get("occupation"),
            data["house_number"],
            purok,
            data.get("contact_number"),
            data.get("email"),
            years_of_residency,
            data.get("voter_status"),
            resident_id
        )
    )

    db.commit()

    db.close()

    return jsonify({
        "message":"Resident updated successfully"
    })


# =====================================================
# ARCHIVE RESIDENT
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>/archive",
    methods=["PUT"]
)
def archive_resident(resident_id):

    db=get_db()

    data = request.json or {}
    reason = data.get("reason")

    if not reason:
        return jsonify({
            "error": "Archive reason is required"
        }), 400

    db.execute(
        """
        UPDATE residents
        SET
            archived=1,
            archived_date=datetime('now'),
            archived_reason=?
        WHERE resident_id=?
        """,
        (reason, resident_id)
    )

    db.commit()

    db.close()

    return jsonify({
        "message":"Resident archived"
    })




# =====================================================
# ARCHIVE REASONS
# =====================================================

@residents_bp.route(
    "/residents/archive/reasons",
    methods=["GET"]
)
def archive_reasons():
    return jsonify([
        "Change of Address / No Longer Staying in the Barangay",
        "Moved Abroad",
        "Deceased",
        "Record Created in Error",
        "Other (Specify)"
    ])


# =====================================================
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>/restore",
    methods=["PUT"]
)
def restore_resident(resident_id):

    db=get_db()

    db.execute(
        """
        UPDATE residents
        SET
            archived=0,
            archived_date=NULL
        WHERE resident_id=?
        """,
        (resident_id,)
    )

    db.commit()

    db.close()

    return jsonify({
        "message":"Resident restored"
    })


# =====================================================
# DELETE RESIDENT
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>",
    methods=["DELETE"]
)
def delete_resident(resident_id):

    db=get_db()

    db.execute(
        """
        DELETE
        FROM residents
        WHERE resident_id=?
        """,
        (resident_id,)
    )

    db.commit()

    db.close()

    return jsonify({
        "message":"Resident deleted"
    })



# =====================================================
# GET ARCHIVED RESIDENTS
# =====================================================

@residents_bp.route(
    "/residents/archive",
    methods=["GET"]
)
def get_archived_residents():

    db = get_db()

    residents = db.execute(
        """
        SELECT *
        FROM residents
        WHERE archived = 1
        ORDER BY archived_date DESC
        """
    ).fetchall()

    db.close()

    return jsonify([
        dict(r)
        for r in residents
    ])


# =====================================================
# GET BASIC RESIDENT
# =====================================================

@residents_bp.route(
    "/residents/<int:resident_id>/basic",
    methods=["GET"]
)
def get_basic_resident(resident_id):

    db = get_db()

    resident = db.execute(
        """
        SELECT
            resident_id,
            first_name,
            middle_name,
            last_name,
            suffix,
            age,
            gender,
            house_number,
            purok,
            status
        FROM residents

        WHERE resident_id = ?
        AND archived = 0
        """,
        (resident_id,)
    ).fetchone()

    db.close()

    if resident is None:
        return jsonify({
            "success": False,
            "message": "Resident not found"
        }), 404

    return jsonify(dict(resident))

    


   