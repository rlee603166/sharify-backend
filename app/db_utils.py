from database import supabase
from schemas import CreateUG, CreateFriendShip
from dependencies import UGRepositoryDep
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


async def add_users_to_groups(
    group_id: int, 
    user_id: int, 
    repo: UGRepositoryDep
):
    return await repo.create(CreateUG(user_id=user_id, group_id=group_id))


async def add_friendship(data: CreateFriendShip):
    return await asyncio.to_thread(
        lambda: supabase.table("friends")\
            .insert(data.model_dump())\
            .execute()
    )


async def check_friendship(user_1: int, user_2: int):
    result = await asyncio.to_thread(
        lambda: supabase.rpc('check_friendship', {
            'user_id_1': user_1,
            'user_id_2': user_2
        }).execute()
    )
    return result


async def get_friendship(user_1: int, user_2: int):
    result = await asyncio.to_thread(
        lambda: supabase.rpc('get_friendship', {
            'user_id_1': user_1,
            'user_id_2': user_2
        }).execute()
    )
    return result.data[0]

async def get_friend_requests(user_id: int):
    result = await asyncio.to_thread(
        lambda: supabase.rpc('get_friend_requests', {
            'id': user_id
        }).execute()
    )
    return result.data
