from Models.Model import Database
from Models.Model import Model


class MatchItem(Model):
    __tablename__ = 'match_items'
    id = Database.Column(Database.Integer, primary_key=True, nullable=False, autoincrement=True)
    match_id = Database.Column(Database.Integer, nullable=False, index=True)
    account_id = Database.Column(Database.BigInteger, nullable=False, index=True)
    player_win = Database.Column(Database.Boolean, nullable=False)
    item_id = Database.Column(Database.Integer, nullable=False)
