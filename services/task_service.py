"""
Task business logic service
"""

from datetime import date, timedelta
from database.db import get_db


class TaskService:
    @staticmethod
    def get_all_tasks(include_archived=False):
        """Get all tasks, optionally including archived"""
        db = get_db()
        if include_archived:
            query = "SELECT * FROM tasks ORDER BY created_at DESC"
        else:
            query = (
                "SELECT * FROM tasks WHERE is_archived = FALSE ORDER BY created_at DESC"
            )

        rows = db.execute(query).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def get_task_by_id(task_id):
        """Get a single task by ID"""
        db = get_db()
        row = db.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
        return dict(row) if row else None

    @staticmethod
    def create_task(data):
        """Create a new task"""
        db = get_db()
        cursor = db.execute(
            """
            INSERT INTO tasks (name, description, metric_type, metric_unit, target_value, frequency, custom_days)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
            (
                data["name"],
                data.get("description"),
                data["metric_type"],
                data.get("metric_unit"),
                data.get("target_value"),
                data["frequency"],
                data.get("custom_days"),
            ),
        )
        db.commit()
        return TaskService.get_task_by_id(cursor.lastrowid)

    @staticmethod
    def update_task(task_id, data):
        """Update an existing task"""
        db = get_db()
        updates = []
        values = []

        allowed_fields = [
            "name",
            "description",
            "metric_unit",
            "target_value",
            "frequency",
            "custom_days",
        ]
        for field in allowed_fields:
            if field in data:
                updates.append(f"{field} = ?")
                values.append(data[field])

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(task_id)
            query = f"UPDATE tasks SET {', '.join(updates)} WHERE id = ?"
            db.execute(query, values)
            db.commit()

        return TaskService.get_task_by_id(task_id)

    @staticmethod
    def delete_task(task_id):
        """Permanently delete a task and its progress logs"""
        db = get_db()
        db.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        db.commit()

    @staticmethod
    def archive_task(task_id):
        """Archive a task (soft delete)"""
        db = get_db()
        db.execute(
            "UPDATE tasks SET is_archived = TRUE, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (task_id,),
        )
        db.commit()

    @staticmethod
    def get_week_start(target_date=None):
        """Get the Sunday that starts the week containing target_date"""
        if target_date is None:
            target_date = date.today()
        elif isinstance(target_date, str):
            target_date = date.fromisoformat(target_date)

        # weekday(): Monday=0, Sunday=6
        days_since_sunday = (target_date.weekday() + 1) % 7
        return target_date - timedelta(days=days_since_sunday)

    @staticmethod
    def get_week_end(target_date=None):
        """Get the Saturday that ends the week containing target_date"""
        week_start = TaskService.get_week_start(target_date)
        return week_start + timedelta(days=6)

    @staticmethod
    def is_scheduled_for_day(task, day_of_week):
        """Check if a task is scheduled for a specific day (0=Sunday, 6=Saturday)"""
        frequency = task["frequency"]

        if frequency == "DAILY":
            return True
        elif frequency == "WEEKDAYS":
            # Monday=1, Friday=5 (our Sunday-based: 1-5)
            return day_of_week in [1, 2, 3, 4, 5]
        elif frequency == "WEEKENDS":
            # Sunday=0, Saturday=6
            return day_of_week in [0, 6]
        elif frequency == "CUSTOM":
            custom_days = task.get("custom_days", "")
            if custom_days:
                days = [int(d) for d in custom_days.split(",")]
                return day_of_week in days
        return False

    @staticmethod
    def get_scheduled_days_for_week(task, week_start):
        """Get list of dates the task is scheduled for in a given week"""
        scheduled = []
        for i in range(7):
            if TaskService.is_scheduled_for_day(task, i):
                scheduled.append(week_start + timedelta(days=i))
        return scheduled
