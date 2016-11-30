from sqlalchemy import Column, BigInteger, Integer, Numeric, ForeignKey
from sqlalchemy.orm import relationship

from Models.Hero import Hero
from Models.Model import Model


class MatchHeroSummary(Model):
    __tablename__ = 'match_hero_summaries'
    account_id = Column(BigInteger, primary_key=True, nullable=False)
    hero_id = Column(Integer, ForeignKey('heroes.hero_id'), primary_key=True, nullable=False)
    player_win = Column(Integer, nullable=False)
    matches = Column(Integer, nullable=False)
    win_rate = Column(Numeric(precision=5, scale=2), nullable=False)
    hero = relationship(Hero)
