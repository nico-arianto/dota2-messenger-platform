from sqlalchemy import Column, Integer, BigInteger, String
from Models.Model import Model

class Player(Model):
    __tablename__ = 'players'
    account_id = Column(BigInteger, primary_key=True, nullable=False)
    steam_id = Column(BigInteger, nullable=False, index=True)
    real_name = Column(String(200), nullable=True)
    persona_name = Column(String(100), nullable=True)
    avatar = Column(String(200), nullable=True)
    profile_url = Column(String(200), nullable=False)
