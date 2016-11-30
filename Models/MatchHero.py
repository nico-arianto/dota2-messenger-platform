from sqlalchemy import Column, Integer, BigInteger, Boolean

from Models.Model import Model


class MatchHero(Model):
    __tablename__ = 'match_heroes'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    match_id = Column(Integer, nullable=False, index=True)
    account_id = Column(BigInteger, nullable=False, index=True)
    player_win = Column(Boolean, nullable=False)
    hero_id = Column(Integer, nullable=False)
