from Models.Model import Database
from Models.Model import Model


class Item(Model):
    __tablename__ = 'items'
    item_id = Database.Column(Database.Integer, primary_key=True, nullable=False)
    item_name = Database.Column(Database.String(100), nullable=True)
    image_url = Database.Column(Database.String(200), nullable=False)
