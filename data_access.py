from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.expression import desc

from Models import Player
from Models import History

from Models import initialise_database

class DataAccess:

    def __init__(self, connection):
        if not connection:
            raise ValueError('Connection string is required!')
        self.connection = connection
        db_engine = create_engine(connection)
        db_session = sessionmaker(bind=db_engine)
        self.session = db_session()

    def initialise_database(self):
        initialise_database(self.connection)

    """
    Player
    """
    def add_player(self, account_id, steam_id, profile_url, real_name=None, persona_name=None, avatar=None):
        new_player = Player(account_id=account_id,
                            steam_id=steam_id,
                            real_name=real_name,
                            persona_name=persona_name,
                            avatar=avatar,
                            profile_url=profile_url)
        self.session.add(new_player)
        self.session.commit()
        return new_player

    def get_player(self, account_id=None, steam_id=None, real_name=None):
        query = self.session.query(Player)
        if account_id:
            return query.filter(Player.account_id == account_id).first()
        elif steam_id:
            return query.filter(Player.steam_id == steam_id).first()
        elif real_name: # limit to 10 players
            LIMIT_PLAYERS = 10
            return query.filter(text('real_name like :real_name')).params(real_name="%" + real_name + "%").limit(LIMIT_PLAYERS).all()
        else:
            raise ValueError('Account id or Steam id or real name must be specified!')

    def update_player(self, player):
        if player is None:
            raise ValueError('Player is required!')
        self.session.add(player)
        self.session.commit()
        return player

    """
    History
    """
    def add_history(self, last_match_id):
        new_history = History(last_match_id=last_match_id)
        self.session.add(new_history)
        self.session.commit()
        return new_history

    def get_last_history(self):
        return self.session.query(History).order_by(desc(History.id)).first()
