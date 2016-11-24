from sqlalchemy import Column, Integer, String, BigInteger
from Models.Model import Model

class Player(Model):
    __tablename__ = 'players'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    account_id = Column(Integer, nullable=False)
    steam_id = Column(BigInteger, nullable=False)
    real_name = Column(String(200), nullable=True)
    persona_name = Column(String(100, convert_unicode=True), nullable=True)
    avatar = Column(String(200), nullable=True)
    profile_url = Column(String(200), nullable=False)
