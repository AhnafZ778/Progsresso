"""
Kanban board service - business logic for to-do items
"""

from datetime import date, timedelta
from database.db import get_db


class KanbanService:
    @staticmethod
    def get_all_items():
        """Get all Kanban items grouped by status"""
        db = get_db()
        rows = db.execute("""
            SELECT * FROM kanban_items 
            ORDER BY status, position, due_date
        """).fetchall()

        items = [dict(row) for row in rows]

        # Convert dates to strings
        for item in items:
            if hasattr(item.get("due_date"), "isoformat"):
                item["due_date"] = item["due_date"].isoformat()

        return {
            "TODO": [i for i in items if i["status"] == "TODO"],
            "IN_PROGRESS": [i for i in items if i["status"] == "IN_PROGRESS"],
            "DONE": [i for i in items if i["status"] == "DONE"],
        }

    @staticmethod
    def get_next_date():
        """Calculate the next available date for a new item"""
        db = get_db()

        # Get the latest due_date from existing items
        row = db.execute("""
            SELECT MAX(due_date) as max_date FROM kanban_items
        """).fetchone()

        if row and row["max_date"]:
            max_date = row["max_date"]
            if hasattr(max_date, "isoformat"):
                last_date = max_date
            else:
                last_date = date.fromisoformat(max_date)
            next_date = last_date + timedelta(days=1)
        else:
            next_date = date.today()

        return next_date

    @staticmethod
    def create_item(data):
        """Create a new Kanban item with auto-assigned date"""
        db = get_db()

        title = data.get("title", "").strip()
        if not title:
            raise ValueError("Title is required")

        description = data.get("description", "").strip() or None

        # Use provided date or auto-assign next date
        if data.get("due_date"):
            due_date = data["due_date"]
        else:
            due_date = KanbanService.get_next_date().isoformat()

        # Use provided status or default to TODO
        status = data.get("status", "TODO").upper()
        # Map lowercase status to uppercase
        status_map = {"todo": "TODO", "doing": "IN_PROGRESS", "done": "DONE"}
        status = status_map.get(status.lower(), status)
        if status not in ("TODO", "IN_PROGRESS", "DONE"):
            status = "TODO"

        # Get next position for target column
        pos_row = db.execute(
            """
            SELECT COALESCE(MAX(position), 0) + 1 as next_pos 
            FROM kanban_items WHERE status = ?
        """,
            (status,),
        ).fetchone()
        position = pos_row["next_pos"]

        cursor = db.execute(
            """
            INSERT INTO kanban_items (title, description, due_date, status, position)
            VALUES (?, ?, ?, ?, ?)
        """,
            (title, description, due_date, status, position),
        )
        db.commit()

        return KanbanService.get_item_by_id(cursor.lastrowid)

    @staticmethod
    def get_item_by_id(item_id):
        """Get a single Kanban item by ID"""
        db = get_db()
        row = db.execute(
            "SELECT * FROM kanban_items WHERE id = ?", (item_id,)
        ).fetchone()
        if row:
            item = dict(row)
            if hasattr(item.get("due_date"), "isoformat"):
                item["due_date"] = item["due_date"].isoformat()
            return item
        return None

    @staticmethod
    def update_item(item_id, data):
        """Update a Kanban item"""
        db = get_db()

        item = KanbanService.get_item_by_id(item_id)
        if not item:
            return None

        updates = []
        values = []

        if "title" in data:
            title = data["title"].strip()
            if not title:
                raise ValueError("Title cannot be empty")
            updates.append("title = ?")
            values.append(title)

        if "description" in data:
            updates.append("description = ?")
            values.append(data["description"].strip() or None)

        if "due_date" in data:
            updates.append("due_date = ?")
            values.append(data["due_date"])

        if "status" in data:
            if data["status"] not in ("TODO", "IN_PROGRESS", "DONE"):
                raise ValueError("Invalid status")
            updates.append("status = ?")
            values.append(data["status"])

        if "position" in data:
            updates.append("position = ?")
            values.append(data["position"])

        if updates:
            updates.append("updated_at = CURRENT_TIMESTAMP")
            values.append(item_id)
            query = f"UPDATE kanban_items SET {', '.join(updates)} WHERE id = ?"
            db.execute(query, values)
            db.commit()

        return KanbanService.get_item_by_id(item_id)

    @staticmethod
    def update_status(item_id, new_status):
        """Quick status update for moving items between columns"""
        if new_status not in ("TODO", "IN_PROGRESS", "DONE"):
            raise ValueError("Invalid status")

        db = get_db()

        # Get next position in target column
        pos_row = db.execute(
            """
            SELECT COALESCE(MAX(position), 0) + 1 as next_pos 
            FROM kanban_items WHERE status = ?
        """,
            (new_status,),
        ).fetchone()
        position = pos_row["next_pos"]

        db.execute(
            """
            UPDATE kanban_items 
            SET status = ?, position = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """,
            (new_status, position, item_id),
        )
        db.commit()

        return KanbanService.get_item_by_id(item_id)

    @staticmethod
    def delete_item(item_id):
        """Delete a Kanban item"""
        db = get_db()
        item = KanbanService.get_item_by_id(item_id)
        if not item:
            return False

        db.execute("DELETE FROM kanban_items WHERE id = ?", (item_id,))
        db.commit()
        return True
