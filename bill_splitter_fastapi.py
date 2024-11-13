from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator
from typing import List, Dict, Optional
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

app = FastAPI(title="Receipt Splitter API",
             description="API for splitting receipts with various methods and additional charges")

class SplitMethod(str, Enum):
    EQUAL = "equal"
    ITEMIZED = "itemized"

class LineItem(BaseModel):
    name: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price: float = Field(gt=0, description="Price must be greater than 0")
    assigned_to: Optional[List[str]] = None

    @validator('price')
    def validate_price(cls, v):
        return round(float(v), 2)

class ReceiptRequest(BaseModel):
    items: List[LineItem]
    additional_charges: Dict[str, float]
    party_size: Optional[int] = Field(gt=0, default=None)
    split_method: SplitMethod = Field(default=SplitMethod.EQUAL)
    assigned_parties: Optional[List[str]] = None

    @validator('additional_charges')
    def validate_charges(cls, v):
        return {k: round(float(amount), 2) for k, amount in v.items()}

    @validator('assigned_parties')
    def validate_assigned_parties(cls, v, values):
        if values.get('split_method') == SplitMethod.ITEMIZED and not v:
            raise ValueError("assigned_parties is required for itemized split")
        return v

class ReceiptProcessor:
    def __init__(self):
        self.decimal_places = 2

    def round_decimal(self, amount: float) -> float:
        """Round amount to specified decimal places."""
        return float(Decimal(str(amount)).quantize(
            Decimal(f'0.{"0" * self.decimal_places}'),
            rounding=ROUND_HALF_UP
        ))

    def calculate_charges_percentage(self, subtotal: float, charges: Dict[str, float]) -> float:
        """Calculate the percentage of additional charges relative to subtotal."""
        total_charges = sum(charges.values())
        return total_charges / subtotal if subtotal > 0 else 0

    def process_equal_split(self, receipt: ReceiptRequest) -> Dict:
        """Process receipt for equal splitting among party."""
        subtotal = sum(item.quantity * item.price for item in receipt.items)
        total_charges = sum(receipt.additional_charges.values())
        total_paid = subtotal + total_charges

        party_size = receipt.party_size or 1
        per_person_base = self.round_decimal(subtotal / party_size)
        per_person_charges = {
            charge_name: self.round_decimal(amount / party_size)
            for charge_name, amount in receipt.additional_charges.items()
        }
        per_person_total = self.round_decimal(total_paid / party_size)

        return {
            "split_method": SplitMethod.EQUAL,
            "subtotal": self.round_decimal(subtotal),
            "charges": {
                name: self.round_decimal(amount)
                for name, amount in receipt.additional_charges.items()
            },
            "total_paid": self.round_decimal(total_paid),
            "per_person": {
                "base_amount": per_person_base,
                "charges": per_person_charges,
                "total": per_person_total
            }
        }

    def process_itemized_split(self, receipt: ReceiptRequest) -> Dict:
        """Process receipt for itemized splitting based on assigned items."""
        person_totals = {person: {"items": [], "subtotal": 0} for person in receipt.assigned_parties}
        
        # Process each line item
        subtotal = 0
        for item in receipt.items:
            item_total = item.quantity * item.price
            subtotal += item_total
            
            assigned_people = item.assigned_to or receipt.assigned_parties
            per_person_amount = self.round_decimal(item_total / len(assigned_people))
            
            for person in assigned_people:
                if person not in person_totals:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Assigned person {person} not in party list"
                    )
                person_totals[person]["subtotal"] += per_person_amount
                person_totals[person]["items"].append({
                    "name": item.name,
                    "quantity": item.quantity,
                    "price": item.price,
                    "share": per_person_amount
                })

        # Calculate additional charges proportion for each person
        total_charges = sum(receipt.additional_charges.values())
        
        # Add proportional charges to each person's total
        for person in person_totals:
            person_subtotal = person_totals[person]["subtotal"]
            person_charges = {
                charge_name: self.round_decimal(amount * (person_subtotal / subtotal))
                for charge_name, amount in receipt.additional_charges.items()
            }
            person_totals[person]["charges"] = person_charges
            person_totals[person]["total"] = self.round_decimal(
                person_subtotal + sum(person_charges.values())
            )

        return {
            "split_method": SplitMethod.ITEMIZED,
            "subtotal": self.round_decimal(subtotal),
            "charges": {
                name: self.round_decimal(amount)
                for name, amount in receipt.additional_charges.items()
            },
            "total_paid": self.round_decimal(subtotal + total_charges),
            "person_totals": person_totals
        }

    def process_receipt(self, receipt: ReceiptRequest) -> Dict:
        """Process receipt based on specified split method."""
        if receipt.split_method == SplitMethod.EQUAL:
            return self.process_equal_split(receipt)
        else:
            return self.process_itemized_split(receipt)

@app.post("/process_receipt")
async def process_receipt(receipt: ReceiptRequest):
    """
    Process a receipt and calculate splits based on the specified method.
    
    - Equal split divides all costs evenly among the party
    - Itemized split allows assigning specific items to specific people
    """
    try:
        processor = ReceiptProcessor()
        result = processor.process_receipt(receipt)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Example models for API documentation
class ExampleResponses:
    equal_split_example = {
        "split_method": "equal",
        "subtotal": 40.00,
        "charges": {
            "tax": 4.00,
            "tip": 8.00,
            "service_fee": 2.00
        },
        "total_paid": 54.00,
        "per_person": {
            "base_amount": 10.00,
            "charges": {
                "tax": 1.00,
                "tip": 2.00,
                "service_fee": 0.50
            },
            "total": 13.50
        }
    }

    itemized_split_example = {
        "split_method": "itemized",
        "subtotal": 45.00,
        "charges": {
            "tax": 4.50,
            "tip": 9.00
        },
        "total_paid": 58.50,
        "person_totals": {
            "Alice": {
                "items": [
                    {
                        "name": "Steak",
                        "quantity": 1,
                        "price": 30.00,
                        "share": 30.00
                    },
                    {
                        "name": "Shared Appetizer",
                        "quantity": 1,
                        "price": 15.00,
                        "share": 5.00
                    }
                ],
                "subtotal": 35.00,
                "charges": {
                    "tax": 3.50,
                    "tip": 7.00
                },
                "total": 45.50
            }
        }
    }

# Add example responses to the API documentation
process_receipt.response_model = Dict
process_receipt.responses = {
    200: {
        "description": "Successful receipt processing",
        "content": {
            "application/json": {
                "examples": {
                    "equal_split": {
                        "summary": "Equal Split Example",
                        "value": ExampleResponses.equal_split_example
                    },
                    "itemized_split": {
                        "summary": "Itemized Split Example",
                        "value": ExampleResponses.itemized_split_example
                    }
                }
            }
        }
    }
}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)