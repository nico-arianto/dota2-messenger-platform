from Models.Model import Database


def initialise_database():
    Database.create_all()
