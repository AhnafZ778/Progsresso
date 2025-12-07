"""
Focus/Pomodoro session service - Supabase version with optional user isolation
"""

from datetime import datetime, date, timedelta
from flask import session
from database.supabase_db import get_supabase


def get_current_user_id():
    """Get the current user's ID from session"""
    return session.get("user_id")


class FocusService:
    # Set to True after running migration_add_user_id.sql
    USER_ISOLATION_ENABLED = True

    @staticmethod
    def start_session(data):
        """Start a new focus session"""
        supabase = get_supabase()
        user_id = get_current_user_id()

        duration = data.get("duration_minutes", 25)
        kanban_item_id = data.get("kanban_item_id")

        insert_data = {
            "kanban_item_id": kanban_item_id,
            "duration_minutes": duration,
            "started_at": datetime.now().isoformat(),
        }

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            insert_data["user_id"] = user_id

        result = supabase.table("focus_sessions").insert(insert_data).execute()

        return result.data[0] if result.data else None

    @staticmethod
    def complete_session(session_id, notes=None):
        """Mark a session as completed"""
        supabase = get_supabase()
        user_id = get_current_user_id()

        query = (
            supabase.table("focus_sessions")
            .update(
                {
                    "is_completed": True,
                    "ended_at": datetime.now().isoformat(),
                    "notes": notes,
                }
            )
            .eq("id", session_id)
        )

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        query.execute()

        return FocusService.get_session_by_id(session_id)

    @staticmethod
    def get_session_by_id(session_id):
        """Get a session by ID"""
        supabase = get_supabase()
        user_id = get_current_user_id()

        query = supabase.table("focus_sessions").select("*").eq("id", session_id)

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        result = query.execute()

        if result.data:
            session_data = result.data[0]
            # Get task info if linked
            if session_data.get("kanban_item_id"):
                task_result = (
                    supabase.table("kanban_items")
                    .select("title")
                    .eq("id", session_data["kanban_item_id"])
                    .execute()
                )
                session_data["task_title"] = (
                    task_result.data[0]["title"] if task_result.data else None
                )
            return session_data
        return None

    @staticmethod
    def get_today_sessions():
        """Get all sessions from today"""
        supabase = get_supabase()
        user_id = get_current_user_id()
        today = date.today().isoformat()

        query = supabase.table("focus_sessions").select("*, kanban_items(title)")

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        result = (
            query.gte("started_at", f"{today}T00:00:00")
            .lte("started_at", f"{today}T23:59:59")
            .order("started_at", desc=True)
            .execute()
        )

        sessions = []
        for row in result.data:
            session_data = {k: v for k, v in row.items() if k != "kanban_items"}
            session_data["task_title"] = (
                row["kanban_items"]["title"] if row.get("kanban_items") else None
            )
            sessions.append(session_data)

        return sessions

    @staticmethod
    def get_total_today():
        """Get total focus time for today in minutes"""
        supabase = get_supabase()
        user_id = get_current_user_id()
        today = date.today().isoformat()

        query = supabase.table("focus_sessions").select("duration_minutes")

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        result = (
            query.gte("started_at", f"{today}T00:00:00")
            .lte("started_at", f"{today}T23:59:59")
            .eq("is_completed", True)
            .execute()
        )

        total = sum(s["duration_minutes"] for s in result.data) if result.data else 0
        return total

    @staticmethod
    def get_stats():
        """Get focus statistics"""
        supabase = get_supabase()
        user_id = get_current_user_id()
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Today's total
        today_total = FocusService.get_total_today()

        # This week's total
        week_query = supabase.table("focus_sessions").select("duration_minutes")

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            week_query = week_query.eq("user_id", user_id)

        week_result = (
            week_query.gte("started_at", f"{week_start.isoformat()}T00:00:00")
            .eq("is_completed", True)
            .execute()
        )

        week_total = (
            sum(s["duration_minutes"] for s in week_result.data)
            if week_result.data
            else 0
        )

        # All time total and count
        all_query = supabase.table("focus_sessions").select(
            "duration_minutes", count="exact"
        )

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            all_query = all_query.eq("user_id", user_id)

        all_result = all_query.eq("is_completed", True).execute()

        all_total = (
            sum(s["duration_minutes"] for s in all_result.data)
            if all_result.data
            else 0
        )
        session_count = all_result.count or 0

        # Streak
        streak = FocusService._calculate_streak()

        return {
            "today_minutes": today_total,
            "today_hours": round(today_total / 60, 1),
            "week_minutes": week_total,
            "week_hours": round(week_total / 60, 1),
            "all_time_minutes": all_total,
            "all_time_hours": round(all_total / 60, 1),
            "total_sessions": session_count,
            "streak_days": streak,
            "motivation_level": FocusService._get_motivation_level(today_total),
        }

    @staticmethod
    def _calculate_streak():
        """Calculate consecutive days with completed sessions"""
        supabase = get_supabase()
        user_id = get_current_user_id()
        streak = 0
        check_date = date.today()

        for _ in range(365):
            day_str = check_date.isoformat()

            query = supabase.table("focus_sessions").select("id", count="exact")

            if FocusService.USER_ISOLATION_ENABLED and user_id:
                query = query.eq("user_id", user_id)

            result = (
                query.gte("started_at", f"{day_str}T00:00:00")
                .lte("started_at", f"{day_str}T23:59:59")
                .eq("is_completed", True)
                .execute()
            )

            if result.count and result.count > 0:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                if check_date == date.today():
                    check_date -= timedelta(days=1)
                    continue
                break

        return streak

    @staticmethod
    def _get_motivation_level(total_minutes):
        """Get motivation level, message, and image based on focus time."""
        if total_minutes < 25:
            return {
                "level": "needs_work",
                "message": "Time to focus! Start a session!",
                "image_url": "/static/icons/icon_rock_lee_sleepy.png",
            }
        elif total_minutes < 50:
            return {
                "level": "good_start",
                "message": "Good start! Keep the momentum going.",
                "image_url": "/static/icons/icon_rock_lee_ready.png",
            }
        elif total_minutes < 100:
            return {
                "level": "gate1",
                "message": "Gate of Opening! The engine is warm.",
                "image_url": "/static/icons/icon_rock_lee_gate1.png",
            }
        elif total_minutes < 150:
            return {
                "level": "gate2",
                "message": "Gate of Healing! Revitalized power!",
                "image_url": "/static/icons/icon_rock_lee_gate2.png",
            }
        elif total_minutes < 200:
            return {
                "level": "gate3",
                "message": "Gate of Life! Use the Hidden Lotus!",
                "image_url": "/static/icons/icon_rock_lee_gate3.png",
            }
        elif total_minutes < 250:
            return {
                "level": "gate4",
                "message": "Gate of Pain! Endure the burn!",
                "image_url": "/static/icons/icon_rock_lee_gate4.png",
            }
        else:
            return {
                "level": "gate5",
                "message": "GATE OF LIMIT! LEGENDARY FOCUS!",
                "image_url": "/static/icons/icon_rock_lee_gate5.png",
            }

    @staticmethod
    def delete_session(session_id):
        """Delete a focus session"""
        supabase = get_supabase()
        user_id = get_current_user_id()

        query = supabase.table("focus_sessions").delete().eq("id", session_id)

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        query.execute()
        return True

    @staticmethod
    def clear_today_sessions():
        """Clear all of today's focus sessions"""
        supabase = get_supabase()
        user_id = get_current_user_id()
        today = date.today().isoformat()

        query = supabase.table("focus_sessions").delete()

        if FocusService.USER_ISOLATION_ENABLED and user_id:
            query = query.eq("user_id", user_id)

        query.gte("started_at", f"{today}T00:00:00").lte(
            "started_at", f"{today}T23:59:59"
        ).execute()
        return True
