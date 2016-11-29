from sqlalchemy import Column, BigInteger, Integer, Numeric
from Models.Model import Model

class MatchSummary(Model):
    __tablename__ = 'match_summaries'
    account_id = Column(BigInteger, primary_key=True, nullable=False)
    player_win = Column(Integer, nullable=False)
    matches = Column(Integer, nullable=False)
    win_rate = Column(Numeric(precision=5, scale=2), nullable=False)
