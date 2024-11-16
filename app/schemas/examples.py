
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