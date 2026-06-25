import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "history.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Create the history table if it doesn't exist."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                city TEXT,
                country TEXT,
                flag TEXT,
                category TEXT,
                description TEXT,
                year_built TEXT,
                latitude REAL,
                longitude REAL,
                image_filename TEXT,
                image_url TEXT,
                confidence REAL,
                source TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def add_history_entry(info: dict, image_filename: str = None, image_url: str = None, confidence: float = 100.0, source: str = "demo"):
    """Insert a new prediction/search result into the history database."""
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO history (
                name, city, country, flag, category, description, year_built,
                latitude, longitude, image_filename, image_url, confidence, source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            info.get("name"),
            info.get("city"),
            info.get("country"),
            info.get("flag", "🌍"),
            info.get("category"),
            info.get("description"),
            info.get("year_built"),
            info.get("latitude"),
            info.get("longitude"),
            image_filename,
            image_url,
            confidence,
            source
        ))
        conn.commit()

def get_recent_history(limit: int = 6):
    """Retrieve the most recent predictions for the homepage."""
    init_db()  # Ensure DB and table exist
    with get_db_connection() as conn:
        rows = conn.execute("""
            SELECT id, name, city, country, flag, image_filename, image_url, confidence, source, timestamp
            FROM history
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(row) for row in rows]

def get_history_entry(entry_id: int):
    """Retrieve a single history record by ID."""
    init_db()  # Ensure DB and table exist
    with get_db_connection() as conn:
        row = conn.execute("SELECT * FROM history WHERE id = ?", (entry_id,)).fetchone()
        return dict(row) if row else None
