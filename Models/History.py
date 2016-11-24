from sqlalchemy import Column, Integer, String
from Models.Model import Model

class History(Model):
    __tablename__ = 'histories'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    last_match_id = Column(Integer, nullable=False)
