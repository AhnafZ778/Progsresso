"""
Task business logic service - Supabase version
"""

from datetime import date, timedelta
from database.supabase_db import get_supabase


class TaskService:
    @staticmethod
    def get_all_tasks(include_archived=False):
        """Get all tasks, optionally including archived"""
        supabase = get_supabase()
        query = supabase.table("tasks").select("*")

        if not include_archived:
            query = query.eq("is_archived", False)

        result = query.order("created_at", desc=True).execute()
        return result.data

    @staticmethod
    def get_task_by_id(task_id):
        """Get a single task by ID"""
        supabase = get_supabase()
        result = supabase.table("tasks").select("*").eq("id", task_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def create_task(data):
        """Create a new task"""
        supabase = get_supabase()
        insert_data = {
            "name": data["name"],
            "description": data.get("description"),
            "metric_type": data["metric_type"],
            "metric_unit": data.get("metric_unit"),
            "target_value": data.get("target_value"),
            "frequency": data["frequency"],
            "custom_days": data.get("custom_days"),
        }
        result = supabase.table("tasks").insert(insert_data).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_task(task_id, data):
        """Update an existing task"""
        supabase = get_supabase()

        allowed_fields = [
            "name",
            "description",
            "metric_unit",
            "target_value",
            "frequency",
            "custom_days",
        ]
        update_data = {k: v for k, v in data.items() if k in allowed_fields}

        if update_data:
            result = (
                supabase.table("tasks").update(update_data).eq("id", task_id).execute()
            )
            return result.data[0] if result.data else None

        return TaskService.get_task_by_id(task_id)

    @staticmethod
    def delete_task(task_id):
        """Permanently delete a task and its progress logs"""
        supabase = get_supabase()
        supabase.table("tasks").delete().eq("id", task_id).execute()

    @staticmethod
    def archive_task(task_id):
        """Archive a task (soft delete)"""
        supabase = get_supabase()
        supabase.table("tasks").update({"is_archived": True}).eq(
            "id", task_id
        ).execute()

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
            return day_of_week in [1, 2, 3, 4, 5]
        elif frequency == "WEEKENDS":
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
