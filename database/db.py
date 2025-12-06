"""
Database connection and initialization for Progresso
"""

import sqlite3
import os
from flask import g, current_app


def get_db():
    """Get database connection for current request"""
    if "db" not in g:
        # Ensure data directory exists
        db_path = current_app.config["DATABASE_PATH"]
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        g.db = sqlite3.connect(db_path, detect_types=sqlite3.PARSE_DECLTYPES)
        g.db.row_factory = sqlite3.Row
        # Enable foreign keys
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


def close_db(e=None):
    """Close database connection"""
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    """Initialize database with schema"""
    db = get_db()
    schema_path = os.path.join(os.path.dirname(__file__), "schema.sql")
    with open(schema_path, "r") as f:
        db.executescript(f.read())
    db.commit()


def init_app(app):
    """Register database functions with Flask app"""
    app.teardown_appcontext(close_db)
