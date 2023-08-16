
from pydantic import BaseModel, NonNegativeInt



class ItemInDB(BaseModel):
    id: int
    name: str
    price: NonNegativeInt
    number: int 
    
    
class ItemIn(BaseModel):
    name: str
    price: NonNegativeInt
    number: int