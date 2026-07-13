import sqlite3
from config import Config


# =====================================================
# DATABASE CONNECTION
# =====================================================

def get_db():
    conn = sqlite3.connect(Config.DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


# =====================================================
# DATABASE QUERY HELPER
# =====================================================

def query_db(query, args=(), one=False):
    db = get_db()

    cursor = db.execute(query, args)
    rows = cursor.fetchall()

    db.commit()
    db.close()

    if one:
        return rows[0] if rows else None

    return rows


def execute(query, args=()):
    db = get_db()
    cursor = db.execute(query, args)
    db.commit()
    db.close()
    return cursor


def fetch_one(query, args=()):
    db = get_db()
    row = db.execute(query, args).fetchone()
    db.close()
    return row


def fetch_all(query, args=()):
    db = get_db()
    rows = db.execute(query, args).fetchall()
    db.close()
    return rows


# =====================================================
# DATABASE INITIALIZATION
# =====================================================

def init_db():

    db = get_db()
    cursor = db.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='residents'")
    residents_exists = cursor.fetchone()

    if residents_exists:
        cursor.execute("PRAGMA table_info(residents)")
        resident_columns = [row[1] for row in cursor.fetchall()]

        expected_columns = [
            "resident_id",
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "birth_date",
            "age",
            "gender",
            "civil_status",
            "nationality",
            "religion",
            "occupation",
            "house_number",
            "purok",
            "contact_number",
            "email",
            "years_of_residency",
            "voter_status",
            "photo",
            "status",
            "archived",
            "archived_date",
            "archived_reason",
            "date_created",
            "date_updated"
        ]

        deprecated_columns = ["residence_start_date"]

        if (
            not all(column in resident_columns for column in expected_columns)
            or any(column in resident_columns for column in deprecated_columns)
        ):
            source_id_column = "id" if "id" in resident_columns else "resident_id"
            source_house_column = "house_number" if "house_number" in resident_columns else "address" if "address" in resident_columns else "''"
            source_purok_column = "purok" if "purok" in resident_columns else "''"
            source_archived_reason_column = "archived_reason" if "archived_reason" in resident_columns else "NULL"

            cursor.executescript("""

            CREATE TABLE residents_new (

                resident_id INTEGER PRIMARY KEY AUTOINCREMENT,

                first_name TEXT NOT NULL,

                middle_name TEXT,

                last_name TEXT NOT NULL,

                suffix TEXT,

                birth_date TEXT NOT NULL,

                age INTEGER NOT NULL,

                gender TEXT NOT NULL,

                civil_status TEXT NOT NULL,

                nationality TEXT DEFAULT 'Filipino',

                religion TEXT,

                occupation TEXT,

                house_number TEXT NOT NULL,

                purok INTEGER NOT NULL,

                contact_number TEXT NOT NULL,

                email TEXT,

                years_of_residency REAL,

                voter_status TEXT DEFAULT 'No',

                photo TEXT,

                status TEXT DEFAULT 'Active',

                archived INTEGER DEFAULT 0,

                archived_date TEXT,

                archived_reason TEXT,

                date_created TEXT DEFAULT (datetime('now')),

                date_updated TEXT DEFAULT (datetime('now'))

            );

            """)

            cursor.execute(f"""
                INSERT INTO residents_new (
                    resident_id,
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
                    photo,
                    status,
                    archived,
                    archived_date,
                    archived_reason,
                    date_created,
                    date_updated
                )
                SELECT
                    {source_id_column},
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
                    COALESCE({source_house_column}, ''),
                    CAST({source_purok_column} AS INTEGER),
                    contact_number,
                    email,
                    CAST(years_of_residency AS REAL),
                    voter_status,
                    photo,
                    status,
                    archived,
                    archived_date,
                    {source_archived_reason_column},
                    date_created,
                    date_updated
                FROM residents
            """)

            cursor.execute("DROP TABLE residents")
            cursor.execute("ALTER TABLE residents_new RENAME TO residents")

    cursor.executescript("""

    -----------------------------------------------------
    -- RESIDENTS
    -----------------------------------------------------

    CREATE TABLE IF NOT EXISTS residents (

        resident_id INTEGER PRIMARY KEY AUTOINCREMENT,

        first_name TEXT NOT NULL,

        middle_name TEXT,

        last_name TEXT NOT NULL,

        suffix TEXT,

        birth_date TEXT NOT NULL,

        age INTEGER NOT NULL,

        gender TEXT NOT NULL,

        civil_status TEXT NOT NULL,

        nationality TEXT DEFAULT 'Filipino',

        religion TEXT,

        occupation TEXT,

        house_number TEXT NOT NULL,

        purok INTEGER NOT NULL,

        contact_number TEXT NOT NULL,

        email TEXT,

        years_of_residency REAL,

        voter_status TEXT DEFAULT 'No',

        photo TEXT,

        status TEXT DEFAULT 'Active',

        archived INTEGER DEFAULT 0,

        archived_date TEXT,

        archived_reason TEXT,

        date_created TEXT DEFAULT (datetime('now')),

        date_updated TEXT DEFAULT (datetime('now'))

    );

    """)

    cursor.execute("DROP TABLE IF EXISTS households")

    db.commit()
    db.close()

    print("Residence Records database initialized successfully.")