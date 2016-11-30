from sqlalchemy import Column, Integer, BigInteger, Boolean

from Models.Model import Model


class MatchItem(Model):
    __tablename__ = 'match_items'
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    match_id = Column(Integer, nullable=False, index=True)
    account_id = Column(BigInteger, nullable=False, index=True)
    player_win = Column(Boolean, nullable=False)
    item_id = Column(Integer, nullable=False)
