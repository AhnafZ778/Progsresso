"""
Progress tracking and statistics service - Supabase version
"""

from datetime import date, timedelta
from database.supabase_db import get_supabase
from services.task_service import TaskService


class ProgressService:
    @staticmethod
    def get_week_progress(date_str=None):
        """Get all progress data for a specific week"""
        week_start = TaskService.get_week_start(date_str)
        week_end = TaskService.get_week_end(date_str)

        supabase = get_supabase()
        tasks = TaskService.get_all_tasks()

        # Get all progress logs for the week
        result = (
            supabase.table("progress_logs")
            .select("*")
            .eq("week_start_date", week_start.isoformat())
            .execute()
        )
        logs = result.data

        logs_by_task = {}
        for log in logs:
            task_id = log["task_id"]
            if task_id not in logs_by_task:
                logs_by_task[task_id] = {}
            log_date = log["log_date"]
            logs_by_task[task_id][log_date] = log

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
        supabase = get_supabase()
        log_date = date.fromisoformat(data["date"])
        week_start = TaskService.get_week_start(log_date)

        # Check if entry already exists
        existing = (
            supabase.table("progress_logs")
            .select("id")
            .eq("task_id", data["task_id"])
            .eq("log_date", data["date"])
            .execute()
        )

        if existing.data:
            # Update existing entry
            log_id = existing.data[0]["id"]
            supabase.table("progress_logs").update(
                {
                    "metric_value": data.get("value"),
                    "notes": data.get("notes"),
                    "is_completed": True,
                }
            ).eq("id", log_id).execute()
        else:
            # Create new entry
            result = (
                supabase.table("progress_logs")
                .insert(
                    {
                        "task_id": data["task_id"],
                        "log_date": data["date"],
                        "week_start_date": week_start.isoformat(),
                        "metric_value": data.get("value"),
                        "notes": data.get("notes"),
                        "is_completed": True,
                    }
                )
                .execute()
            )
            log_id = result.data[0]["id"] if result.data else None

        return ProgressService.get_log_by_id(log_id)

    @staticmethod
    def get_log_by_id(log_id):
        """Get a progress log by ID"""
        supabase = get_supabase()
        result = supabase.table("progress_logs").select("*").eq("id", log_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_progress(log_id, data):
        """Update a progress log entry"""
        supabase = get_supabase()

        update_data = {}
        if "value" in data:
            update_data["metric_value"] = data["value"]
        if "notes" in data:
            update_data["notes"] = data["notes"]
        if "is_completed" in data:
            update_data["is_completed"] = data["is_completed"]

        if update_data:
            supabase.table("progress_logs").update(update_data).eq(
                "id", log_id
            ).execute()

        return ProgressService.get_log_by_id(log_id)

    @staticmethod
    def delete_progress(log_id):
        """Delete a progress log entry"""
        supabase = get_supabase()
        supabase.table("progress_logs").delete().eq("id", log_id).execute()
        return True

    @staticmethod
    def calculate_health_score(task_id):
        """
        Calculate health score based on 14-day completion rate and trend.
        Returns: float between 0.0 (poor) and 1.0 (excellent)
        """
        supabase = get_supabase()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return 0.5

        today = date.today()
        fourteen_days_ago = today - timedelta(days=14)

        # Get all logs for last 14 days
        result = (
            supabase.table("progress_logs")
            .select("log_date, is_completed")
            .eq("task_id", task_id)
            .gte("log_date", fourteen_days_ago.isoformat())
            .eq("is_completed", True)
            .execute()
        )

        completed_dates = {log["log_date"] for log in result.data}

        # Calculate scheduled vs completed
        scheduled_count = 0
        completed_count = 0
        recent_scheduled = 0
        recent_completed = 0
        older_scheduled = 0
        older_completed = 0

        for i in range(14):
            check_date = today - timedelta(days=i)
            day_of_week = (check_date.weekday() + 1) % 7

            if TaskService.is_scheduled_for_day(task, day_of_week):
                scheduled_count += 1
                is_recent = i < 7

                if is_recent:
                    recent_scheduled += 1
                else:
                    older_scheduled += 1

                if check_date.isoformat() in completed_dates:
                    completed_count += 1
                    if is_recent:
                        recent_completed += 1
                    else:
                        older_completed += 1

        if scheduled_count == 0:
            return 0.5

        completion_rate = completed_count / scheduled_count
        recent_rate = recent_completed / recent_scheduled if recent_scheduled > 0 else 0
        older_rate = older_completed / older_scheduled if older_scheduled > 0 else 0
        trend_bonus = (recent_rate - older_rate) * 0.2

        return max(0.0, min(1.0, completion_rate + trend_bonus))

    @staticmethod
    def get_task_stats(task_id):
        """Get comprehensive statistics for a task"""
        supabase = get_supabase()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return None

        health_score = ProgressService.calculate_health_score(task_id)

        # Get total completions
        total_result = (
            supabase.table("progress_logs")
            .select("id", count="exact")
            .eq("task_id", task_id)
            .eq("is_completed", True)
            .execute()
        )
        total_count = total_result.count or 0

        # Get all values for average
        values_result = (
            supabase.table("progress_logs")
            .select("metric_value")
            .eq("task_id", task_id)
            .not_.is_("metric_value", "null")
            .execute()
        )

        values = [
            v["metric_value"]
            for v in values_result.data
            if v["metric_value"] is not None
        ]
        avg_value = sum(values) / len(values) if values else None

        streak = ProgressService.calculate_streak(task_id)

        return {
            "task_id": task_id,
            "health_score": health_score,
            "total_completions": total_count,
            "average_value": avg_value,
            "current_streak": streak,
        }

    @staticmethod
    def calculate_streak(task_id):
        """Calculate current consecutive completion streak"""
        supabase = get_supabase()
        task = TaskService.get_task_by_id(task_id)
        if not task:
            return 0

        # Get all completed logs ordered by date desc
        result = (
            supabase.table("progress_logs")
            .select("log_date")
            .eq("task_id", task_id)
            .eq("is_completed", True)
            .order("log_date", desc=True)
            .execute()
        )

        completed_dates = {log["log_date"] for log in result.data}

        streak = 0
        check_date = date.today()

        for _ in range(365):
            day_of_week = (check_date.weekday() + 1) % 7

            if TaskService.is_scheduled_for_day(task, day_of_week):
                if check_date.isoformat() in completed_dates:
                    streak += 1
                else:
                    if check_date == date.today():
                        check_date -= timedelta(days=1)
                        continue
                    break

            check_date -= timedelta(days=1)

        return streak

    @staticmethod
    def get_summary(weeks=4):
        """Get summary data for the specified number of weeks"""
        supabase = get_supabase()
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

            weekly_data = []
            for w in range(weeks):
                week_start = TaskService.get_week_start(today - timedelta(weeks=w * 7))

                result = (
                    supabase.table("progress_logs")
                    .select("metric_value, is_completed")
                    .eq("task_id", task["id"])
                    .eq("week_start_date", week_start.isoformat())
                    .execute()
                )
                logs = result.data

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
