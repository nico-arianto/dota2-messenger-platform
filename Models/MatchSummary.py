from sqlalchemy import Column, BigInteger, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from Models.Model import Model
from Models.Player import Player


class MatchSummary(Model):
    __tablename__ = 'match_summaries'
    account_id = Column(BigInteger, ForeignKey("players.account_id"), primary_key=True, nullable=False)
    player_win = Column(Integer, nullable=False)
    matches = Column(Integer, nullable=False)
    win_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    player = relationship(Player)
