"""
Progresso - Weekly Habit Tracker Web Application
Main Flask Application Entry Point
"""

from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()  # Load .env file before anything else

from flask import Flask, render_template
from config import Config
from database.supabase_db import init_app as init_supabase_app


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Session configuration for "Stay logged in"
    app.config["PERMANENT_SESSION_LIFETIME"] = timedelta(days=30)

    # Initialize Supabase
    init_supabase_app(app)

    # Import and register blueprints
    from routes.auth import auth_bp, login_required
    from routes.tasks import tasks_bp
    from routes.progress import progress_bp
    from routes.reports import reports_bp
    from routes.kanban import kanban_bp
    from routes.focus import focus_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(kanban_bp)
    app.register_blueprint(focus_bp)

    # Main route - protected
    @app.route("/")
    @login_required
    def index():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5500)
