import os
import asyncio
from typing import Optional, List
from pydantic import BaseModel
from fastapi import HTTPException
from schemas import UserInDB, UserCreate, GetFriends
from PIL import Image, ExifTags
from io import BytesIO
from datetime import datetime
import uuid

class UserService:
    def __init__(self, repository, auth, friend_repo):
        self.repository = repository
        self.auth_service = auth
        self.friend_repo = friend_repo
        self.pwd = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            ), 
            "storage/pfp/"
        )
    
    async def standardize(self, image_data):
        content = await image_data.read()

        image = Image.open(BytesIO(content))
     
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break

            exif = image._getexif()
            if exif is not None:
                if orientation in exif:
                    if exif[orientation] == 3:
                        image = image.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        image = image.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        image = image.rotate(90, expand=True)

        except (AttributeError, KeyError, IndexError, TypeError):
            pass       

        if image.mode != "RGB":
            image = image.convert("RGB")
        
        output_buffer = BytesIO()
        image.save(output_buffer, format='PNG')

        return output_buffer.getvalue()

    def create_pfp_filepath(self):
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())
        extension = "png"

        return f"{timestamp}_{unique_id}.{extension}"


    async def save_image(self, image_data, filepath):
        try:
            path = self.pwd + filepath;
            img = Image.open(BytesIO(image_data))
            await asyncio.to_thread(img.save, path)
        except Exception as e:
            print(f'Error saving image: {e}')


    async def get_all_users(self) -> List[UserInDB]:
        return await self.repository.get_all()

    async def get_by_phone(self, phone: str):
        existing_user = await self.repository.get_by_phone(phone)
        if existing_user:
            return True
        else:
            return False
           
    async def get_user(self, username: str) -> Optional[UserInDB]:
        try:
            return await self.repository.get_by_username(username)
        except HTTPException as e:
            if e.status_code == 404:
                return None
            raise

    async def create_user(self, user: UserCreate):
        return await self.repository.create(user)


    async def get_friends(self, user_id: int):
        friends = await self.friend_repo.get_by_user(user_id)

        if friends is None:
            return "no friends"

        friend_ids =  [
            GetFriends(user_1=friend["user_1"], friend_id=friend["friend_id"]) 
            if friend["user_1"] != user_id else GetFriends(user_1=friend["user_2"], friend_id=friend["friend_id"])
            for friend in friends
        ]
        

        tasks = [self.repository.get(friend.user_1) for friend in friend_ids]

        friends = await asyncio.gather(*tasks)

        result = []

        for i, friend in enumerate(friends):
            result.append(UserInDB(
                user_id=friend["user_id"],
                name=friend["name"],
                username=friend["username"],
                phone=friend["phone"],
                created_at=friend["created_at"],
                imageUri=friend["imageUri"],
                friend_id=friend_ids[i].friend_id
            ))

        return result


