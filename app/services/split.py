from schemas import SplitCreate, Item

class SplitService():
    def __init__(self, split_repo):
        self.split_repo = split_repo

    async def upload(self, receipt_id, data):
        try:
            items_list = []
            for item in data.items:
                if hasattr(item, 'model_dump'):
                    temp = item.model_dump()
                else:
                    temp = {
                        "name": item.name,
                        "price": item.price,
                        "totalPrice": item.totalPrice
                    }
                items_list.append(temp)
        
            print("Creating SplitCreate with:")
            print(f"receipt_id: {receipt_id}")
            print(f"items_list: {items_list}")
            print(f"subtotal: {data.subtotal}")
            print(f"tax: {data.tax}")
            print(f"tip: {data.tip}")
            print(f"misc: {data.misc}")
            print(f"total: {data.finalTotal}")
        
            split = SplitCreate(
                receipt_id=receipt_id,
                user_id=1,
                subtotal=data.subtotal,
                items=items_list,
                tax=data.tax,
                tip=data.tip,
                misc=data.misc,
                total=data.finalTotal
            )
            return await self.split_repo.create(split)
        except Exception as e:
            print(f"Error in upload: {e}")
            raise
        

    async def get_by_user_id(self, username):
        return await self.split_repo.get_by_user_id(username)
 
