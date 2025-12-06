"""
Kanban board service - Supabase version
"""

from datetime import date, timedelta
from database.supabase_db import get_supabase


class KanbanService:
    @staticmethod
    def get_all_items():
        """Get all Kanban items grouped by status"""
        supabase = get_supabase()
        result = (
            supabase.table("kanban_items")
            .select("*")
            .order("status")
            .order("position")
            .order("due_date")
            .execute()
        )

        items = result.data

        return {
            "TODO": [i for i in items if i["status"] == "TODO"],
            "IN_PROGRESS": [i for i in items if i["status"] == "IN_PROGRESS"],
            "DONE": [i for i in items if i["status"] == "DONE"],
        }

    @staticmethod
    def get_next_date():
        """Calculate the next available date for a new item"""
        supabase = get_supabase()

        result = (
            supabase.table("kanban_items")
            .select("due_date")
            .order("due_date", desc=True)
            .limit(1)
            .execute()
        )

        if result.data and result.data[0]["due_date"]:
            last_date = date.fromisoformat(result.data[0]["due_date"])
            next_date = last_date + timedelta(days=1)
        else:
            next_date = date.today()

        return next_date

    @staticmethod
    def create_item(data):
        """Create a new Kanban item with auto-assigned date"""
        supabase = get_supabase()

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
        status_map = {"todo": "TODO", "doing": "IN_PROGRESS", "done": "DONE"}
        status = status_map.get(status.lower(), status)
        if status not in ("TODO", "IN_PROGRESS", "DONE"):
            status = "TODO"

        # Get next position for target column
        pos_result = (
            supabase.table("kanban_items")
            .select("position")
            .eq("status", status)
            .order("position", desc=True)
            .limit(1)
            .execute()
        )

        position = (pos_result.data[0]["position"] + 1) if pos_result.data else 1

        result = (
            supabase.table("kanban_items")
            .insert(
                {
                    "title": title,
                    "description": description,
                    "due_date": due_date,
                    "status": status,
                    "position": position,
                }
            )
            .execute()
        )

        return result.data[0] if result.data else None

    @staticmethod
    def get_item_by_id(item_id):
        """Get a single Kanban item by ID"""
        supabase = get_supabase()
        result = supabase.table("kanban_items").select("*").eq("id", item_id).execute()
        return result.data[0] if result.data else None

    @staticmethod
    def update_item(item_id, data):
        """Update a Kanban item"""
        supabase = get_supabase()

        item = KanbanService.get_item_by_id(item_id)
        if not item:
            return None

        update_data = {}

        if "title" in data:
            title = data["title"].strip()
            if not title:
                raise ValueError("Title cannot be empty")
            update_data["title"] = title

        if "description" in data:
            update_data["description"] = data["description"].strip() or None

        if "due_date" in data:
            update_data["due_date"] = data["due_date"]

        if "status" in data:
            if data["status"] not in ("TODO", "IN_PROGRESS", "DONE"):
                raise ValueError("Invalid status")
            update_data["status"] = data["status"]

        if "position" in data:
            update_data["position"] = data["position"]

        if update_data:
            result = (
                supabase.table("kanban_items")
                .update(update_data)
                .eq("id", item_id)
                .execute()
            )
            return result.data[0] if result.data else None

        return KanbanService.get_item_by_id(item_id)

    @staticmethod
    def update_status(item_id, new_status):
        """Quick status update for moving items between columns"""
        if new_status not in ("TODO", "IN_PROGRESS", "DONE"):
            raise ValueError("Invalid status")

        supabase = get_supabase()

        # Get next position in target column
        pos_result = (
            supabase.table("kanban_items")
            .select("position")
            .eq("status", new_status)
            .order("position", desc=True)
            .limit(1)
            .execute()
        )

        position = (pos_result.data[0]["position"] + 1) if pos_result.data else 1

        result = (
            supabase.table("kanban_items")
            .update(
                {
                    "status": new_status,
                    "position": position,
                }
            )
            .eq("id", item_id)
            .execute()
        )

        return result.data[0] if result.data else None

    @staticmethod
    def delete_item(item_id):
        """Delete a Kanban item"""
        supabase = get_supabase()
        item = KanbanService.get_item_by_id(item_id)
        if not item:
            return False

        supabase.table("kanban_items").delete().eq("id", item_id).execute()
        return True
