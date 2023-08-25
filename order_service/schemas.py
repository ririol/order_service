import datetime
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
    

class OrderInDB(BaseModel):
    id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime
    title: str
    total: NonNegativeInt
    items: list[ItemInDB]


class OrderIn(BaseModel):
    title: str
    items: list[ItemIn]


class Statistic(BaseModel):
    total_orders: int
    total_order_price: int
    avg_order_price: int
    total_items: int
    avg_items: int
    most_ordered_item: str