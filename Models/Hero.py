from sqlalchemy import Column, Integer, String
from Models.Model import Model

class Hero(Model):
    __tablename__ = 'heroes'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    hero_id = Column(Integer, nullable=False, index=True)
    hero_name = Column(String(100), nullable=True)
    portrait_url = Column(String(200), nullable=False)
