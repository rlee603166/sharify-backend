import json
import re
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from dependencies import ReceiptProcessorDep

class Prompt(BaseModel):
    prompt: str

router = APIRouter(
    prefix="/receipts",
    tags=["receipts"]
)


@router.post(
    "/process",
)
async def process_receipt(
    request: Prompt,
    service: ReceiptProcessorDep
):
    """
    Process a receipt and calculate splits based on the specified method.
    
    - Equal split divides all costs evenly among the party
    - Itemized split allows assigning specific items to specific people
    """
    try:    
        result = await service.process_receipt(request.prompt)
        clean_response = re.sub(r'```(?:json|javascript)?\n?(.*?)\n?```', r'\1', result, flags=re.DOTALL)
        
        # Try to fix common JSON formatting issues
        clean_response = clean_response.strip()
        if not clean_response.startswith('{'):
            clean_response = '{' + clean_response + '}'
        
        # Convert any remaining JavaScript-style object to valid JSON
        clean_response = re.sub(r'(?m)^(\s*)(\w+):', r'\1"\2":', clean_response)
        
        # Parse the cleaned response
        parsed_data = json.loads(clean_response)

        return parsed_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


