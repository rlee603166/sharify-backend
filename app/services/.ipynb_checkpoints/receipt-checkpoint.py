import re
import json
from openai import OpenAI
from dotenv import load_dotenv
import pytesseract
import cv2

load_dotenv()

class ReceiptProcessor:
    def __init__(self) -> None:
        self.client = OpenAI()

    def ocr(self, image_path):
        try:
        # Read the image
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"Image not found at path: {image_path}")

        # Convert the image to RGB format
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform OCR
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            return f"Error processing the image: {str(e)}"

    async def get_completion(self, prompt, model="gpt-4"):
        try:
            completion = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": prompt}
                        ]
                    )
            return completion.choices[0].message.content
        except Exception as e:
            return f"An error occurred: {str(e)}"


    async def process_receipt(self, image_path):
        """
        Process a receipt image and extract structured data.

        Args:
            image_path (str): Path to the receipt image file.

        Returns:
            dict: Parsed transaction data or an error message.
        """
        try:
            # Step 1: Extract text using OCR
            extracted_text = self.ocr(image_path)
            
            # Step 2: Send prompt to GPT model
            completion = self.client.chat.completions.create(
                model="gpt-3.5-turbo",  # Replace with the appropriate model
                messages=[
                    {
                        "role": "system",
                        "content": "You are an assistant that formats receipt data into a structured format for a food-sharing app."
                    },
                    {
                        "role": "user",
                        "content": f"""
                        The following is text extracted from a receipt. Extract the items and prices and format them as an array of objects with this structure:

                        items: [
                            {{
                                id: "<unique_id>",
                                name: "<item_name>",
                                price: <price>,
                                people: []
                            }},
                            ...
                        ]

                        Use an incrementing numeric ID for each item, starting from 1. Ensure the names and prices are accurate.

                        Text:
                        {extracted_text}
                        """
                    }
                ],
                max_tokens=500
            )

            raw_response = completion.choices[0].message.content

            return raw_response

        except FileNotFoundError:
            return {"error": f"Image file not found: {image_path}"}
        except json.JSONDecodeError as e:
            return {"error": f"Failed to parse JSON response: {str(e)}", "raw_response": raw_response}
        except Exception as e:
            return {"error": f"Processing failed: {str(e)}"}
