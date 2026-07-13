import requests
from database import get_db

def get_total_certificates():
    db = get_db()
    try:
        table_exists = db.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='certificates'"
        ).fetchone()

        if table_exists is None:
            return 0

        row = db.execute("SELECT COUNT(*) AS total FROM certificates").fetchone()
        return int(row["total"]) if row else 0
    finally:
        db.close()


def fetch_total_certificates_from_api():
    response = requests.get(
        f"{SERVER_URL}/api/certificates/total",
        timeout=5
    )

    if response.status_code != 200:
        return 0

    return response.json().get("total_certificates", 0)