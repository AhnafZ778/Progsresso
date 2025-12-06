"""
Progresso - Weekly Habit Tracker Web Application
Main Flask Application Entry Point
"""

from flask import Flask, render_template
from config import Config
from database.supabase_db import init_app as init_supabase_app


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize Supabase
    init_supabase_app(app)

    # Import and register blueprints
    from routes.tasks import tasks_bp
    from routes.progress import progress_bp
    from routes.reports import reports_bp
    from routes.kanban import kanban_bp
    from routes.focus import focus_bp

    app.register_blueprint(tasks_bp)
    app.register_blueprint(progress_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(kanban_bp)
    app.register_blueprint(focus_bp)

    # Main route
    @app.route("/")
    def index():
        return render_template("index.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5500)
