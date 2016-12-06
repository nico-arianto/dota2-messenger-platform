from Models.Model import Database
from Models.Model import Model


class Hero(Model):
    __tablename__ = 'heroes'
    hero_id = Database.Column(Database.Integer, primary_key=True, nullable=False)
    hero_name = Database.Column(Database.String(100), nullable=True)
    portrait_url = Database.Column(Database.String(200), nullable=False)
