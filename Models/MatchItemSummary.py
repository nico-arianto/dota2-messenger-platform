from sqlalchemy import Column, BigInteger, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from Models.Model import Model
from Models.Item import Item

class MatchItemSummary(Model):
    __tablename__ = 'match_item_summaries'
    account_id = Column(BigInteger, primary_key=True, nullable=False)
    item_id = Column(Integer, ForeignKey('items.item_id'), primary_key=True, nullable=False)
    player_win = Column(Integer, nullable=False)
    matches = Column(Integer, nullable=False)
    win_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    item = relationship(Item)
