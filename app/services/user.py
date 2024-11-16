from database import get_users as db_get_users

class UserService:
    @staticmethod
    async def get_all_users():
        return await db_get_users()

    @staticmethod
    def get_user_items(username: str):
        return [{"item_id": "Foo", "owner": username}]
