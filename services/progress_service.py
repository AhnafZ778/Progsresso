"""
Progress tracking and statistics service
"""

from datetime import date, timedelta
from database.db import get_db
from services.task_service import TaskService


class ProgressService:
    @staticmethod
    def get_week_progress(date_str=None):
        """Get all progress data for a specific week"""
        week_start = TaskService.get_week_start(date_str)
        week_end = TaskService.get_week_end(date_str)

        db = get_db()
        tasks = TaskService.get_all_tasks()

        # Get all progress logs for the week
        logs = db.execute(
            """
            SELECT * FROM progress_logs 
            WHERE week_start_date = ?
        """,
            (week_start.isoformat(),),
        ).fetchall()

        logs_by_task = {}
        for log in logs:
            log_dict = dict(log)
            task_id = log_dict["task_id"]
            if task_id not in logs_by_task:
                logs_by_task[task_id] = {}
            # Convert log_date to string if it's a date object
            log_date = log_dict["log_date"]
            if hasattr(log_date, "isoformat"):
                log_date = log_date.isoformat()
            log_dict["log_date"] = log_date  # Ensure consistent format in response
            logs_by_task[task_id][log_date] = log_dict

        # Build week data structure
        week_data = {
            "week_start": week_start.isoformat(),
            "week_end": week_end.isoformat(),
            "tasks": [],
        }

        for task in tasks:
            task_data = {
                **task,
                "days": [],
                "health_score": ProgressService.calculate_health_score(task["id"]),
            }

            for i in range(7):
                day_date = week_start + timedelta(days=i)
                day_str = day_date.isoformat()
                is_scheduled = TaskService.is_scheduled_for_day(task, i)

                day_data = {
                    "date": day_str,
                    "day_name": day_date.strftime("%a"),
                    "is_scheduled": is_scheduled,
                    "is_today": day_date == date.today(),
                    "is_past": day_date < date.today(),
                    "log": None,
                }

                if task["id"] in logs_by_task and day_str in logs_by_task[task["id"]]:
                    day_data["log"] = logs_by_task[task["id"]][day_str]

                task_data["days"].append(day_data)

            week_data["tasks"].append(task_data)

        return week_data

    @staticmethod
    def log_progress(data):
        """Create or update a progress log entry"""
        db = get_db()
        log_date = date.fromisoformat(data["date"])
        week_start = TaskService.get_week_start(log_date)

        # Check if entry already exists
        existing = db.execute(
            """
            SELECT id FROM progress_logs WHERE task_id = ? AND log_date = ?
        """,
            (data["task_id"], data["date"]),
        ).fetchone()

        if existing:
            # Update existing entry
            db.execute(
                """
                UPDATE progress_logs 
                SET metric_value = ?, notes = ?, is_completed = TRUE, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """,
                (data.get("value"), data.get("notes"), existing["id"]),
            )
            db.commit()
            log_id = existing["id"]
        else:
            # Create new entry
            cursor = db.execute(
                """
                INSERT INTO progress_logs (task_id, log_date, week_start_date, metric_value, notes, is_completed)
                VALUES (?, ?, ?, ?, ?, TRUE)
            """,
                (
                    data["task_id"],
                    data["date"],
                    week_start.isoformat(),
                    data.get("value"),
                    data.get("notes"),
                ),
            )
            db.commit()
            log_id = cursor.lastrowid

        return ProgressService.get_log_by_id(log_id)

    @staticmethod
    def get_log_by_id(log_id):
        """Get a progress log by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM progress_logs WHERE id = ?", (log_id,)
        ).fetchone()
        return dict(row) if row else None

    @staticmethod
    def update_progress(log_id, data):
        """Update a progress log entry"""
        db = get_db()
        updates = []
        values = []

        if "value" in data:
            updates.append("metric_value = ?")
            values.append(data["value"])
        if "notes" in data:
            updates.append("notes = ?")
            values.append(data["notes"])
        if "is_completed" in data:
            updates.append("is_completed = ?")
            values.append(data["is_completed"])

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(log_id)
            query = f"UPDATE progress_logs SET {', '.join(updates)} WHERE id = ?"
            db.execute(query, values)
            db.commit()

        return ProgressService.get_log_by_id(log_id)

    @staticmethod
    def calculate_health_score(task_id):
        """
        Calculate health score based on 14-day completion rate and trend.
        Returns: float between 0.0 (poor) and 1.0 (excellent)
        """
        db = get_db()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return 0.5

        today = date.today()
        fourteen_days_ago = today - timedelta(days=14)
        seven_days_ago = today - timedelta(days=7)

        # Get scheduled days in the last 14 days
        scheduled_count = 0
        completed_count = 0
        recent_scheduled = 0
        recent_completed = 0
        older_scheduled = 0
        older_completed = 0

        for i in range(14):
            check_date = today - timedelta(days=i)
            day_of_week = (check_date.weekday() + 1) % 7  # Convert to Sunday=0

            if TaskService.is_scheduled_for_day(task, day_of_week):
                scheduled_count += 1
                if i < 7:
                    recent_scheduled += 1
                else:
                    older_scheduled += 1

                # Check if completed
                log = db.execute(
                    """
                    SELECT is_completed FROM progress_logs 
                    WHERE task_id = ? AND log_date = ? AND is_completed = TRUE
                """,
                    (task_id, check_date.isoformat()),
                ).fetchone()

                if log:
                    completed_count += 1
                    if i < 7:
                        recent_completed += 1
                    else:
                        older_completed += 1

        if scheduled_count == 0:
            return 0.5  # Neutral for new tasks

        completion_rate = completed_count / scheduled_count

        # Calculate trend bonus
        recent_rate = recent_completed / recent_scheduled if recent_scheduled > 0 else 0
        older_rate = older_completed / older_scheduled if older_scheduled > 0 else 0
        trend_bonus = (recent_rate - older_rate) * 0.2  # ±20% adjustment

        return max(0.0, min(1.0, completion_rate + trend_bonus))

    @staticmethod
    def get_task_stats(task_id):
        """Get comprehensive statistics for a task"""
        db = get_db()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return None

        health_score = ProgressService.calculate_health_score(task_id)

        # Get total completions
        total = db.execute(
            """
            SELECT COUNT(*) as count FROM progress_logs 
            WHERE task_id = ? AND is_completed = TRUE
        """,
            (task_id,),
        ).fetchone()

        # Get average value (for non-boolean tasks)
        avg = db.execute(
            """
            SELECT AVG(metric_value) as avg_value FROM progress_logs 
            WHERE task_id = ? AND metric_value IS NOT NULL
        """,
            (task_id,),
        ).fetchone()

        # Calculate current streak
        streak = ProgressService.calculate_streak(task_id)

        return {
            "task_id": task_id,
            "health_score": health_score,
            "total_completions": total["count"],
            "average_value": avg["avg_value"],
            "current_streak": streak,
        }

    @staticmethod
    def calculate_streak(task_id):
        """Calculate current consecutive completion streak"""
        db = get_db()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return 0

        streak = 0
        check_date = date.today()

        for _ in range(365):  # Check up to a year back
            day_of_week = (check_date.weekday() + 1) % 7

            if TaskService.is_scheduled_for_day(task, day_of_week):
                log = db.execute(
                    """
                    SELECT is_completed FROM progress_logs 
                    WHERE task_id = ? AND log_date = ? AND is_completed = TRUE
                """,
                    (task_id, check_date.isoformat()),
                ).fetchone()

                if log:
                    streak += 1
                else:
                    # If it's today and not completed yet, don't break the streak
                    if check_date == date.today():
                        check_date -= timedelta(days=1)
                        continue
                    break

            check_date -= timedelta(days=1)

        return streak

    @staticmethod
    def get_summary(weeks=4):
        """Get summary data for the specified number of weeks"""
        db = get_db()
        tasks = TaskService.get_all_tasks()
        today = date.today()
        start_date = TaskService.get_week_start(today - timedelta(weeks=weeks * 7))

        summary = {
            "period_start": start_date.isoformat(),
            "period_end": today.isoformat(),
            "total_tasks": len(tasks),
            "tasks": [],
        }

        for task in tasks:
            stats = ProgressService.get_task_stats(task["id"])

            # Get weekly breakdown
            weekly_data = []
            for w in range(weeks):
                week_start = TaskService.get_week_start(today - timedelta(weeks=w * 7))
                logs = db.execute(
                    """
                    SELECT metric_value, is_completed FROM progress_logs 
                    WHERE task_id = ? AND week_start_date = ?
                """,
                    (task["id"], week_start.isoformat()),
                ).fetchall()

                completed = sum(1 for log in logs if log["is_completed"])
                values = [
                    log["metric_value"]
                    for log in logs
                    if log["metric_value"] is not None
                ]

                weekly_data.append(
                    {
                        "week_start": week_start.isoformat(),
                        "completed_days": completed,
                        "values": values,
                        "avg_value": sum(values) / len(values) if values else None,
                    }
                )

            summary["tasks"].append({**task, **stats, "weekly_data": weekly_data})

        return summary
