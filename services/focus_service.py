"""
Focus/Pomodoro session service - business logic for focus timer
"""

from datetime import datetime, date, timedelta
from database.db import get_db


class FocusService:
    @staticmethod
    def start_session(data):
        """Start a new focus session"""
        db = get_db()

        duration = data.get("duration_minutes", 25)
        kanban_item_id = data.get("kanban_item_id")

        cursor = db.execute(
            """
            INSERT INTO focus_sessions (kanban_item_id, duration_minutes, started_at)
            VALUES (?, ?, ?)
        """,
            (kanban_item_id, duration, datetime.now().isoformat()),
        )
        db.commit()

        return FocusService.get_session_by_id(cursor.lastrowid)

    @staticmethod
    def complete_session(session_id, notes=None):
        """Mark a session as completed"""
        db = get_db()

        db.execute(
            """
            UPDATE focus_sessions 
            SET is_completed = TRUE, ended_at = ?, notes = ?
            WHERE id = ?
        """,
            (datetime.now().isoformat(), notes, session_id),
        )
        db.commit()

        return FocusService.get_session_by_id(session_id)

    @staticmethod
    def get_session_by_id(session_id):
        """Get a session by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM focus_sessions WHERE id = ?", (session_id,)
        ).fetchone()
        if row:
            session = dict(row)
            # Get task info if linked
            if session.get("kanban_item_id"):
                task = db.execute(
                    "SELECT title FROM kanban_items WHERE id = ?",
                    (session["kanban_item_id"],),
                ).fetchone()
                session["task_title"] = task["title"] if task else None
            return session
        return None

    @staticmethod
    def get_today_sessions():
        """Get all sessions from today"""
        db = get_db()
        today = date.today().isoformat()

        rows = db.execute(
            """
            SELECT fs.*, ki.title as task_title
            FROM focus_sessions fs
            LEFT JOIN kanban_items ki ON fs.kanban_item_id = ki.id
            WHERE DATE(fs.started_at) = ?
            ORDER BY fs.started_at DESC
        """,
            (today,),
        ).fetchall()

        return [dict(row) for row in rows]

    @staticmethod
    def get_total_today():
        """Get total focus time for today in minutes"""
        db = get_db()
        today = date.today().isoformat()

        row = db.execute(
            """
            SELECT COALESCE(SUM(duration_minutes), 0) as total
            FROM focus_sessions 
            WHERE DATE(started_at) = ? AND is_completed = TRUE
        """,
            (today,),
        ).fetchone()

        return row["total"]

    @staticmethod
    def get_stats():
        """Get focus statistics"""
        db = get_db()
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Today's total
        today_total = FocusService.get_total_today()

        # This week's total
        week_row = db.execute(
            """
            SELECT COALESCE(SUM(duration_minutes), 0) as total
            FROM focus_sessions 
            WHERE DATE(started_at) >= ? AND is_completed = TRUE
        """,
            (week_start.isoformat(),),
        ).fetchone()
        week_total = week_row["total"]

        # All time total
        all_row = db.execute("""
            SELECT COALESCE(SUM(duration_minutes), 0) as total,
                   COUNT(*) as session_count
            FROM focus_sessions WHERE is_completed = TRUE
        """).fetchone()
        all_total = all_row["total"]
        session_count = all_row["session_count"]

        # Streak (consecutive days with sessions)
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
        db = get_db()
        streak = 0
        check_date = date.today()

        for _ in range(365):
            row = db.execute(
                """
                SELECT COUNT(*) as count FROM focus_sessions 
                WHERE DATE(started_at) = ? AND is_completed = TRUE
            """,
                (check_date.isoformat(),),
            ).fetchone()

            if row["count"] > 0:
                streak += 1
                check_date -= timedelta(days=1)
            else:
                # If it's today and no sessions yet, don't break streak
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
        db = get_db()
        db.execute("DELETE FROM focus_sessions WHERE id = ?", (session_id,))
        db.commit()
        return True

    @staticmethod
    def clear_today_sessions():
        """Clear all of today's focus sessions"""
        db = get_db()
        today = date.today().isoformat()
        db.execute("DELETE FROM focus_sessions WHERE DATE(started_at) = ?", (today,))
        db.commit()
        return True
