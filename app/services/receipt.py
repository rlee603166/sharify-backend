import re
import os
import base64
import json
import asyncio
import uuid
import requests
from datetime import datetime
from openai import OpenAI
from PIL import Image, ExifTags
import numpy as np
from dotenv import load_dotenv
from schemas import ReceiptCreate, ReceiptUpdate
import pytesseract
import cv2
from io import BytesIO

load_dotenv()

class ReceiptProcessor:
    def __init__(self, repository) -> None:
        self.client = OpenAI()
        self.repository = repository 
        self.pwd = os.path.join(
            os.path.dirname(
                os.path.dirname(os.path.dirname(__file__))
            ), 
            "storage/receipts/"
        )


    def create_filepath(self, user_id):
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())
        extension = "png"

        return f"{user_id}_{timestamp}_{unique_id}.{extension}"


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


    async def save_image(self, image_data, filepath):
        try:
            img = Image.open(BytesIO(image_data))
            await asyncio.to_thread(img.save, filepath)
        except Exception as e:
            print(f'Error saving image: {e}')


    async def upload(self, data):
        return await self.repository.create(ReceiptCreate(**data))


    def resize(self, image):
        max_dimension = 2000
        height, width = image.shape[:2]
        if max(height, width) > max_dimension:
            scale = max_dimension / max(height, width)
            width = int(width * scale)
            height = int(height * scale)
            return cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return image

    
    def enhance(self, image):
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        enhanced = clahe.apply(gray)
        denoised = cv2.fastNlMeansDenoising(enhanced)
        return denoised


    def threshold(self, image):
        binary = cv2.adaptiveThreshold(
            image, 
            255, 
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 
            21,  # block size
            11   # C constant
        )
        kernel = np.ones((2,2), np.uint8)
        cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
    
        return cleaned


    def deskew(self, image):
        coords = np.column_stack(np.where(image > 0))

        angle = cv2.minAreaRect(coords)[-1]

        if angle < -45:
            angle = 90 + angle

        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                 flags=cv2.INTER_CUBIC,
                                 borderMode=cv2.BORDER_REPLICATE)
        return rotated


    def preprocess(self, image):
        resized = self.resize(image)

        enhanced = self.enhance(resized)

        binary = self.threshold(enhanced)

        return binary

    def clean_text(self, text):
        text = ' '.join(text.split())
    
        text = re.sub(r'[=|]', '', text)
        text = re.sub(r'\s+', ' ', text)
    
        lines = [line.strip() for line in text.split('\n') if line.strip()]
    
        cleaned_text = '\n'.join(lines)
    
        return cleaned_text

    def process(self, receipt_id, image_path):
        url = "http://0.0.0.0:8001/gpt"
        payload = {
            "receipt_id": receipt_id,
            "path": image_path
        }
        print("fetching second process")
        x = requests.post(url, json=payload)

    async def save_and_process(self, png, filepath):
        path = self.pwd + filepath
        await self.save_image(png, path)

        receipt = await self.repository.get_by_path(filepath)
        print(receipt)
        asyncio.create_task(asyncio.to_thread(self.process, receipt["receipt_id"], filepath))
