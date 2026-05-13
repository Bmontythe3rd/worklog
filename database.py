import sqlite3
from pathlib import Path

DB_PATH = Path.home() / ".worklog" / "worklog.db"

PRESET_CATEGORIES = [
    "Feature", "Bug Fix", "Code Review", "Meeting",
    "Documentation", "Deployment", "Testing", "Research",
    "Refactor", "Incident Response", "Other",
]


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS entries (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                title       TEXT NOT NULL,
                description TEXT,
                project     TEXT,
                category    TEXT,
                created_at  TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at  TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def _row_factory(conn):
    conn.row_factory = sqlite3.Row
    return conn


def get_all_entries(start_date=None, end_date=None, project=None):
    with _row_factory(sqlite3.connect(DB_PATH)) as conn:
        query = "SELECT * FROM entries WHERE 1=1"
        params = []
        if start_date:
            query += " AND date >= ?"
            params.append(start_date)
        if end_date:
            query += " AND date <= ?"
            params.append(end_date)
        if project:
            query += " AND project = ?"
            params.append(project)
        query += " ORDER BY date DESC, id DESC"
        return conn.execute(query, params).fetchall()


def get_entry(entry_id):
    with _row_factory(sqlite3.connect(DB_PATH)) as conn:
        return conn.execute("SELECT * FROM entries WHERE id = ?", (entry_id,)).fetchone()


def create_entry(date, title, description, project, category):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.execute(
            "INSERT INTO entries (date, title, description, project, category) VALUES (?, ?, ?, ?, ?)",
            (date, title, description or None, project or None, category or None),
        )
        conn.commit()
        return cursor.lastrowid


def update_entry(entry_id, date, title, description, project, category):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute(
            """UPDATE entries
               SET date=?, title=?, description=?, project=?, category=?,
                   updated_at=CURRENT_TIMESTAMP
               WHERE id=?""",
            (date, title, description or None, project or None, category or None, entry_id),
        )
        conn.commit()


def delete_entry(entry_id):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("DELETE FROM entries WHERE id = ?", (entry_id,))
        conn.commit()


def get_projects():
    with sqlite3.connect(DB_PATH) as conn:
        rows = conn.execute(
            "SELECT DISTINCT project FROM entries WHERE project IS NOT NULL AND project != '' ORDER BY project"
        ).fetchall()
        return [row[0] for row in rows]


def get_entry_count():
    with sqlite3.connect(DB_PATH) as conn:
        return conn.execute("SELECT COUNT(*) FROM entries").fetchone()[0]
