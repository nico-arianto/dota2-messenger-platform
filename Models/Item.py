from sqlalchemy import Column, Integer, String
from Models.Model import Model

class Item(Model):
    __tablename__ = 'items'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    item_id = Column(Integer, nullable=False, index=True)
    item_name = Column(String(100), nullable=True)
    image_url = Column(String(200), nullable=False)
