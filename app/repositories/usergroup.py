from . import BaseRepository
from database import supabase
from schemas import CreateUG, UpdateUG

class UGRepository(BaseRepository[dict, CreateUG, UpdateUG]):
    def __init__(self):
        super().__init__(supabase, "users_groups", pk="")

    async def delete_by_user_group(self, user_id: int, group_id: int):
        try:
            response = (
                self.db.table(self.table_name)
                .delete()
                .eq("user_id", user_id)
                .eq("group_id", group_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                return True
            else:
                return False  

        except Exception as e:
            print(f"Error fetching user-group record: {e}")
            raise
