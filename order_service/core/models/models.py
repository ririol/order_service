from sqlalchemy import Column, Integer, String, DateTime , ForeignKey
import datetime
from .database import Base

metadata = Base.metadata

class Item(Base):
    __tablename__ = 'items'
    id = Column( Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    price = Column(Integer)
    number = Column(Integer)
    order_id = Column(Integer, ForeignKey('order.id'))


class Order(Base):
    __tablename__ = 'order'
    id = Column(Integer, primary_key=True, autoincrement=True)
    created_date = Column( DateTime , default=datetime.datetime.utcnow())
    updated_date = Column( DateTime , default=datetime.datetime.utcnow(), onupdate=datetime.datetime.utcnow())
    title = Column(String)
    total = Column(Integer)
    


