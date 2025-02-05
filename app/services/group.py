import os
import asyncio
import uuid
from datetime import datetime
from PIL import Image, ExifTags
from io import BytesIO
from schemas import CreateGroup


class GroupService:
    def __init__(self, repo) -> None:
        self.repo = repo 
        self.pwd = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            ), 
            "storage/groups/"
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

    def create_group_filepath(self):
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


    async def create(self, group: CreateGroup):
        return await self.repo.create(group)
