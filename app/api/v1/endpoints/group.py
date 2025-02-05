from fastapi import APIRouter, UploadFile, BackgroundTasks
from db_utils import *
from dependencies import GroupServiceDep, GroupRepositoryDep, UGRepositoryDep
from schemas import CreateGroup, UpdateGroup, NewGroup, CreateUG
import asyncio


router = APIRouter(
    prefix="/groups",
    tags=["groups"]
)

async def add_to_ug(group_id, members, repo):
    for member in members:
        await add_users_to_groups(group_id, member.user_id, repo)

@router.post("/")
async def create_group(
    group_data: NewGroup,
    service: GroupServiceDep, repo: UGRepositoryDep,
    background_tasks: BackgroundTasks
):
    new_group = CreateGroup(group_name=group_data.group_name, imageUri=group_data.imageUri)

    created_group = await service.create(new_group)

    background_tasks.add_task(add_to_ug, created_group['group_id'], group_data.members, repo)

    return created_group

@router.delete("/user")
async def delete_ug(
    user_group: CreateUG,
    repo: UGRepositoryDep
):
    return await repo.delete_by_user_group(user_group.user_id, user_group.group_id)


@router.post("/upload-image")
async def upload_image(
    image: UploadFile, 
    service: GroupServiceDep,
    background_tasks: BackgroundTasks
):
    png = await service.standardize(image)
    filepath = service.create_group_filepath()
    
    background_tasks.add_task(service.save_image, png, filepath)

    return { 'filepath': filepath }


@router.get("/{group_id}")
async def group(group_id: int):
    group = await get_group(group_id)
    return group.data


@router.patch("/{group_id}")
async def update(group_id: int, data: UpdateGroup, repo: GroupRepositoryDep):
    return await repo.update(group_id, data)


@router.get("/user/{user_id}")
async def get_groups_by_user(user_id: int):
    groups = await get_user_groups(user_id)
    group_data = groups.data

    print(group_data)

    member_data = await asyncio.gather(
        *[get_group(g["group_id"]) for g in group_data]
    )

    return [{
        "group_id": group["group_id"],
        "name": group["groups"]["group_name"],
        "members": member.data,
        "imageUri": group["groups"]["imageUri"]
    } for group, member in zip(group_data, member_data)]
