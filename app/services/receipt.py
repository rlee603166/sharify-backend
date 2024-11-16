from decimal import Decimal, ROUND_HALF_UP
from typing import Dict
from fastapi import HTTPException
from schemas import ReceiptRequest, SplitMethod

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