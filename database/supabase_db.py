"""
Supabase database connection for Progresso
Replaces SQLite with PostgreSQL via Supabase
"""

import os
from supabase import create_client, Client
from flask import g, current_app


def get_supabase() -> Client:
    """Get Supabase client for current request"""
    if "supabase" not in g:
        url = current_app.config.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
        key = current_app.config.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

        if not url or not key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

        g.supabase = create_client(url, key)
    return g.supabase


def init_app(app):
    """Register cleanup function with Flask app"""

    @app.teardown_appcontext
    def close_supabase(e=None):
        g.pop("supabase", None)
