from Models.Model import Database
from Models.Model import Model
from Models.Player import Player


class MatchSummary(Model):
    __tablename__ = 'match_summaries'
    account_id = Database.Column(Database.BigInteger, Database.ForeignKey("players.account_id"), primary_key=True,
                                 nullable=False)
    player_win = Database.Column(Database.Integer, nullable=False)
    matches = Database.Column(Database.Integer, nullable=False)
    win_rate = Database.Column(Database.Numeric(precision=5, scale=2), nullable=False)
    player = Database.relationship(Player)
