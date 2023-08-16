from pydantic import BaseModel, NonNegativeInt
import datetime
from .item import ItemInDB, ItemIn


class OrderInDB(BaseModel):
    id: int
    create_date: datetime.datetime
    update_date: datetime.datetime
    tittle: str
    total: NonNegativeInt
    items: list[ItemInDB]


class OrderIn(BaseModel):
    tittle: str
    items: list[ItemIn]
