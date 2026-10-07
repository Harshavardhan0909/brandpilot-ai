from pathlib import Path
import sqlite3
import uuid
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parents[1] / "brandpilot.db"


def connect():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with connect() as db:
        db.executescript(
            """
            CREATE TABLE IF NOT EXISTS brands (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL,
                industry TEXT NOT NULL,
                target_audience TEXT NOT NULL,
                tone_of_voice TEXT NOT NULL,
                primary_colors TEXT NOT NULL,
                forbidden_words TEXT NOT NULL,
                preferred_words TEXT NOT NULL,
                created_at TEXT NOT NULL
            );
            CREATE TABLE IF NOT EXISTS guidelines (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                source_name TEXT NOT NULL,
                content TEXT NOT NULL,
                created_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            );
            CREATE TABLE IF NOT EXISTS campaigns (
                id TEXT PRIMARY KEY,
                brand_id TEXT NOT NULL,
                objective TEXT NOT NULL,
                product TEXT NOT NULL,
                audience TEXT NOT NULL,
                platform TEXT NOT NULL,
                status TEXT NOT NULL,
                result_json TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (brand_id) REFERENCES brands(id)
            );
            """
        )


def now():
    return datetime.now(timezone.utc).isoformat()


def new_id(prefix):
    return f"{prefix}_{uuid.uuid4().hex[:12]}"
