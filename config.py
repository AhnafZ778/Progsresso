"""
Progspresso Configuration
Settings for the Flask application
"""

import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class Config:
    """Application configuration"""

    SECRET_KEY = os.environ.get("SECRET_KEY") or "progresso-dev-key-2025"
    DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

    # Supabase configuration (set these in environment variables)
    SUPABASE_URL = os.environ.get("SUPABASE_URL")
    SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
