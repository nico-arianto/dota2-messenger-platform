from Models.Item import Item
from Models.Model import Database
from Models.Model import Model


class MatchItemSummary(Model):
    __tablename__ = 'match_item_summaries'
    account_id = Database.Column(Database.BigInteger, primary_key=True, nullable=False)
    item_id = Database.Column(Database.Integer, Database.ForeignKey('items.item_id'), primary_key=True, nullable=False)
    player_win = Database.Column(Database.Integer, nullable=False)
    matches = Database.Column(Database.Integer, nullable=False)
    win_rate = Database.Column(Database.Numeric(precision=5, scale=2), nullable=False)
    item = Database.relationship(Item)
