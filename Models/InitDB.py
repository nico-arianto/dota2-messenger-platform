from sqlalchemy import create_engine

from Models.Model import Model


def initialise_database(engine):
    db_engine = create_engine(engine, echo=True)
    Model.metadata.create_all(db_engine)
