"""
Supabase database connection for Progresso
Replaces SQLite with PostgreSQL via Supabase
"""

import os
from supabase import create_client, Client
from flask import g, current_app


def get_supabase(use_auth: bool = True) -> Client:
    """Get Supabase client for current request.

    Args:
        use_auth: If True, authenticate the client with the user's access token
                  so that RLS policies using auth.uid() work correctly.
    """
    url = current_app.config.get("SUPABASE_URL") or os.environ.get("SUPABASE_URL")
    key = current_app.config.get("SUPABASE_KEY") or os.environ.get("SUPABASE_KEY")

    if not url or not key:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set")

    # Create a new client or get the existing one
    if "supabase" not in g:
        g.supabase = create_client(url, key)

    # Set the user's access token on the postgrest client headers
    # This is critical for RLS policies to work correctly with auth.uid()
    if use_auth:
        from flask import session

        access_token = session.get("access_token")
        user_id = session.get("user_id")

        print(
            f"[DEBUG get_supabase] user_id={user_id}, has_access_token={bool(access_token)}"
        )

        if access_token:
            # Set the Authorization header for postgrest requests
            # This makes auth.uid() return the correct user ID in RLS policies
            g.supabase.postgrest.auth(access_token)
            print(f"[DEBUG get_supabase] Auth header set on postgrest client")

    return g.supabase


def init_app(app):
    """Register cleanup function with Flask app"""

    @app.teardown_appcontext
    def close_supabase(e=None):
        g.pop("supabase", None)
