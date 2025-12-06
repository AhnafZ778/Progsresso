"""
Focus/Pomodoro session service - Supabase version
"""

from datetime import datetime, date, timedelta
from database.supabase_db import get_supabase


class FocusService:
    @staticmethod
    def start_session(data):
        """Start a new focus session"""
        supabase = get_supabase()

        duration = data.get("duration_minutes", 25)
        kanban_item_id = data.get("kanban_item_id")

        result = (
            supabase.table("focus_sessions")
            .insert(
                {
                    "kanban_item_id": kanban_item_id,
                    "duration_minutes": duration,
                    "started_at": datetime.now().isoformat(),
                }
            )
            .execute()
        )

        return result.data[0] if result.data else None

    @staticmethod
    def complete_session(session_id, notes=None):
        """Mark a session as completed"""
        supabase = get_supabase()

        supabase.table("focus_sessions").update(
            {
                "is_completed": True,
                "ended_at": datetime.now().isoformat(),
                "notes": notes,
            }
        ).eq("id", session_id).execute()

        return FocusService.get_session_by_id(session_id)

    @staticmethod
    def get_session_by_id(session_id):
        """Get a session by ID"""
        supabase = get_supabase()
        result = (
            supabase.table("focus_sessions").select("*").eq("id", session_id).execute()
        )

        if result.data:
            session = result.data[0]
            # Get task info if linked
            if session.get("kanban_item_id"):
                task_result = (
                    supabase.table("kanban_items")
                    .select("title")
                    .eq("id", session["kanban_item_id"])
                    .execute()
                )
                session["task_title"] = (
                    task_result.data[0]["title"] if task_result.data else None
                )
            return session
        return None

    @staticmethod
    def get_today_sessions():
        """Get all sessions from today"""
        supabase = get_supabase()
        today = date.today().isoformat()

        # Get sessions with task info via join
        result = (
            supabase.table("focus_sessions")
            .select("*, kanban_items(title)")
            .gte("started_at", f"{today}T00:00:00")
            .lte("started_at", f"{today}T23:59:59")
            .order("started_at", desc=True)
            .execute()
        )

        sessions = []
        for row in result.data:
            session = {k: v for k, v in row.items() if k != "kanban_items"}
            session["task_title"] = (
                row["kanban_items"]["title"] if row.get("kanban_items") else None
            )
            sessions.append(session)

        return sessions

    @staticmethod
    def get_total_today():
        """Get total focus time for today in minutes"""
        supabase = get_supabase()
        today = date.today().isoformat()

        result = (
            supabase.table("focus_sessions")
            .select("duration_minutes")
            .gte("started_at", f"{today}T00:00:00")
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
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Today's total
        today_total = FocusService.get_total_today()

        # This week's total
        week_result = (
            supabase.table("focus_sessions")
            .select("duration_minutes")
            .gte("started_at", f"{week_start.isoformat()}T00:00:00")
            .eq("is_completed", True)
            .execute()
        )
        week_total = (
            sum(s["duration_minutes"] for s in week_result.data)
            if week_result.data
            else 0
        )

        # All time total and count
        all_result = (
            supabase.table("focus_sessions")
            .select("duration_minutes", count="exact")
            .eq("is_completed", True)
            .execute()
        )
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
        streak = 0
        check_date = date.today()

        for _ in range(365):
            day_str = check_date.isoformat()
            result = (
                supabase.table("focus_sessions")
                .select("id", count="exact")
                .gte("started_at", f"{day_str}T00:00:00")
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
        supabase.table("focus_sessions").delete().eq("id", session_id).execute()
        return True

    @staticmethod
    def clear_today_sessions():
        """Clear all of today's focus sessions"""
        supabase = get_supabase()
        today = date.today().isoformat()
        supabase.table("focus_sessions").delete().gte(
            "started_at", f"{today}T00:00:00"
        ).lte("started_at", f"{today}T23:59:59").execute()
        return True
