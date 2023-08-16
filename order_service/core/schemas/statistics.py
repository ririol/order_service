from pydantic import BaseModel


class Statistic(BaseModel):
    total_orders: int
    total_order_price: int
    avg_order_price: int
    total_items: int
    avg_items: int
    most_ordered_item: str