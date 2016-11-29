from sqlalchemy import Column, Integer, String
from Models.Model import Model

class Item(Model):
    __tablename__ = 'items'
    item_id = Column(Integer, primary_key=True, nullable=False)
    item_name = Column(String(100), nullable=True)
    image_url = Column(String(200), nullable=False)
