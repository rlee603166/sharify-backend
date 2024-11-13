from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# Define a Pydantic model for line items
class LineItem(BaseModel):
    name: str
    quantity: int
    price: float

# Define a Pydantic model for receipt data
class ReceiptData(BaseModel):
    items: List[LineItem]
    tax: float
    cc_fee: float
    tip: float
    party_size: Optional[int] = 1  # Optional, defaults to 1

def process_receipt(receipt_data: ReceiptData):
    """
    Process receipt data to calculate subtotal, distribute charges proportionally,
    calculate total amount owed for each line item, and optionally divide total by party size.
    """
    # Calculate the subtotal from the list of items
    subtotal = sum(item.quantity * item.price for item in receipt_data.items)
    if subtotal == 0:
        raise HTTPException(status_code=400, detail="Subtotal cannot be zero.")

    # Calculate the total charges and their respective percentages
    total_charges = receipt_data.tax + receipt_data.cc_fee + receipt_data.tip
    total_percentage = total_charges / subtotal if subtotal > 0 else 0

    # Distribute the total charges proportionally to each line item
    processed_items = []
    for item in receipt_data.items:
        item_total_price = item.quantity * item.price
        total_with_charges = item_total_price + (item_total_price * total_percentage)

        processed_items.append({
            "name": item.name,
            "quantity": item.quantity,
            "price": item.price,
            "total_with_charges": round(total_with_charges, 2)
        })

    # Calculate total paid and per-person cost if party size is specified
    total_paid = subtotal + total_charges
    per_person_cost = round(total_paid / receipt_data.party_size, 2) if receipt_data.party_size > 0 else total_paid

    result = {
        "subtotal": round(subtotal, 2),
        "tax": receipt_data.tax,
        "cc_fee": receipt_data.cc_fee,
        "tip": receipt_data.tip,
        "total_paid": round(total_paid, 2),
        "per_person_cost": per_person_cost,
        "items": processed_items
    }
    return result

@app.post("/process_receipt")
def process_receipt_endpoint(receipt_data: ReceiptData):
    # Process the receipt data
    result = process_receipt(receipt_data)
    return result
