from pydantic import BaseModel, NonNegativeInt
import datetime
from .item import ItemInDB, ItemIn
from typing import Optional


class OrderInDB(BaseModel):
    id: int
    created_date: datetime.datetime
    updated_date: datetime.datetime
    title: str
    total: NonNegativeInt
    items: Optional[list[ItemInDB]]


class OrderIn(BaseModel):
    title: str
    items: list[ItemIn]
