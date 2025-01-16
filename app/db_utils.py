from database import supabase
import asyncio

async def get_user_groups(user_id: int):
    return await asyncio.to_thread( 
        lambda: supabase.table("users_groups")\
            .select("*, groups(*)")\
            .eq("user_id", user_id)\
            .execute() 
    )


async def get_group(group_id: int):
    return await asyncio.to_thread( 
        lambda: supabase.table("users_groups")\
            .select("*, users(*)")\
            .eq("group_id", group_id)\
            .execute() 
    )
