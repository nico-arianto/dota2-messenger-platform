from Models.Hero import Hero
from Models.Model import Database
from Models.Model import Model


class MatchHeroSummary(Model):
    __tablename__ = 'match_hero_summaries'
    account_id = Database.Column(Database.BigInteger, primary_key=True, nullable=False)
    hero_id = Database.Column(Database.Integer, Database.ForeignKey('heroes.hero_id'), primary_key=True, nullable=False)
    player_win = Database.Column(Database.Integer, nullable=False)
    matches = Database.Column(Database.Integer, nullable=False)
    win_rate = Database.Column(Database.Numeric(precision=5, scale=2), nullable=False)
    hero = Database.relationship(Hero)
