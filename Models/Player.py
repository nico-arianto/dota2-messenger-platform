from Models.Model import Database
from Models.Model import Model


class Player(Model):
    __tablename__ = 'players'
    account_id = Database.Column(Database.BigInteger, primary_key=True, nullable=False)
    steam_id = Database.Column(Database.BigInteger, nullable=False, index=True)
    real_name = Database.Column(Database.String(200), nullable=True)
    persona_name = Database.Column(Database.String(100), nullable=True)
    avatar = Database.Column(Database.String(200), nullable=True)
    profile_url = Database.Column(Database.String(200), nullable=False)
