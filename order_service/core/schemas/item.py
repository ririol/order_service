from pydantic import BaseModel, NonNegativeInt


class ItemInDB(BaseModel):
    id: int
    name: str
    price: NonNegativeInt
    number: int
    order_id: int
    
    
class ItemIn(BaseModel):
    name: str
    price: NonNegativeInt
    number: int