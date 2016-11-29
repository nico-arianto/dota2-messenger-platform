from sqlalchemy import Column, Integer, String
from Models.Model import Model

class Hero(Model):
    __tablename__ = 'heroes'
    hero_id = Column(Integer, primary_key=True, nullable=False)
    hero_name = Column(String(100), nullable=True)
    portrait_url = Column(String(200), nullable=False)
