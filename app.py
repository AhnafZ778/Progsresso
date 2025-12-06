"""
HabitPulse - Weekly Habit Tracker Web Application
Main Flask Application Entry Point
"""

import os
from flask import Flask, render_template, send_from_directory
from config import Config
from database.db import init_db, init_app as init_db_app
from routes.tasks import tasks_bp
from routes.progress import progress_bp
from routes.reports import reports_bp
from routes.kanban import kanban_bp
from routes.focus import focus_bp


def create_app():
    """Application factory"""
    app = Flask(__name__)
    app.config.from_object(Config)

    # Ensure data directory exists
    os.makedirs(os.path.dirname(app.config["DATABASE_PATH"]), exist_ok=True)

    # Initialize database
    init_db_app(app)

    with app.app_context():
        init_db()

    # Register blueprints
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
