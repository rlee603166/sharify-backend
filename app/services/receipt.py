import re
import json
import asyncio
import uuid
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
        self.pwd = "/home/sush/divvy/divvy-backend/storage"


    def create_filepath(self, user_id):
        timestamp = datetime.now().strftime('%Y%m%d')
        unique_id = str(uuid.uuid4())
        extension = "png"

        return f"{self.pwd}/{user_id}_{timestamp}_{unique_id}.{extension}"


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

    def ocr(self, image_path):
        try:
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Image not found at path: {image_path}")

            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image = self.preprocess(image)

            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error processing the image: {str(e)}"


    def clean_text(self, text):
        text = ' '.join(text.split())
    
        text = re.sub(r'[=|]', '', text)
        text = re.sub(r'\s+', ' ', text)
    
        lines = [line.strip() for line in text.split('\n') if line.strip()]
    
        cleaned_text = '\n'.join(lines)
    
        return cleaned_text


    async def process(self, image_path):
        try:
            extracted_text = self.ocr(image_path)

            completion = self.client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that formats receipt data into a structured format for a food-sharing app."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        The following is text extracted from a receipt. Extract the items and prices and return them as JSON with this exact structure:
                        {{
                            "items": [
                                {{
                                    "id": "<unique_id>",
                                    "name": "<item_name>",
                                    "price": <price>,
                                    "people": []
                                }}
                            ],
                            "additional": [
                                {{
                                    "tax": <tax>,
                                    "tip": <tip>,
                                    "credit_charge": <credit_charge>
                                }}
                            ]
                        }}
                        Use an incrementing numeric ID for each item, starting from 1. Ensure the names and prices are accurate.

                        Receipt text:
                        {extracted_text}
                        """
                    }
                ],
                max_tokens=500,
                response_format={ "type": "json_object" }
            )

            raw_response = completion.choices[0].message.content

            response = json.loads(raw_response)

            return response, extracted_text

        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}", "raw_response": raw_response}
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}

    async def save_and_process(self, png, filepath):
        await self.save_image(png, filepath)

        (processed_data, extracted_text), receipt = await asyncio.gather(
            self.process(filepath),
            self.repository.get_by_path(filepath)
        )

        update_data = ReceiptUpdate(
            processed_data=processed_data,
            extracted_text=extracted_text,
            status="completed"
        )

        await self.repository.update(receipt["receipt_id"], update_data)
