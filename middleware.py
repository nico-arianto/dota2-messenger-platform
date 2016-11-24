import dota2api
from sqlalchemy.exc import DatabaseError

from data_access import DataAccess
import logger

import config

LOGGER = logger.getLogger(__name__)
API = dota2api.Initialise(api_key=config.dota2api['D2_API_KEY'])
DATA = DataAccess(connection=config.mysql['CONNECT_STRING'])

"""
Metadata
"""
def initialise_database():
    DATA.initialise_database()

"""
ETL
"""
def fill_database():
    last_history = DATA.get_last_history()

    start_at_match_seq_num = None
    if last_history:
        start_at_match_seq_num = last_history.last_match_id
    LOGGER.info('ETL start from math id: %s', str(start_at_match_seq_num))

    next_match_history = API.get_match_history_by_seq_num(start_at_match_seq_num=start_at_match_seq_num)
    if next_match_history is None:
        return
    elif next_match_history['status'] != 1:
        raise ValueError(next_match_history['statusDetail'])

    last_match = None
    account_ids = []
    for match in next_match_history['matches']:
        last_match = match['match_id']
        for player in match['players']:
            if 'account_id' not in player:
                continue
            account_id = player['account_id']
            if account_id not in account_ids:
                __fill_player(account_id=account_id)
                account_ids.append(account_id)

    DATA.add_history(last_match_id=last_match)
    LOGGER.info('ETL finish with math id: %s', str(last_match))

def __fill_player(account_id):
    LOGGER.info('Find account id: %s', str(account_id))
    # Important: Cannot utilize steamids with account_ids, because the orders of returned players was not in the same sequence.
    players = API.get_player_summaries(steamids=account_id)
    if players is None:
        LOGGER.info('Not found account id: %s', str(account_id))
        return
    for player in players['players']:
        steam_id = player['steamid']
        real_name = player.get('realname', None)
        persona_name = player.get('personaname', None)
        avatar = player.get('avatarfull', None)
        profile_url = player.get('profileurl', None)
        data_player = DATA.get_player(account_id=account_id)
        try:
            if data_player is None:
                DATA.add_player(account_id=account_id,
                                steam_id=steam_id,
                                profile_url=profile_url,
                                real_name=real_name,
                                persona_name=persona_name,
                                avatar=avatar)
                LOGGER.info('Created account id: %s', str(account_id))
            else:
                data_player.steam_id = steam_id
                data_player.real_name = real_name
                data_player.persona_name = persona_name
                data_player.avatar = avatar
                data_player.profile_url = profile_url
                DATA.update_player(player=data_player)
                LOGGER.info('Updated account id: %s', str(account_id))
        except DatabaseError as error: # TODO: Temporary ignore the unsupported data, especially the unicode issue.
            LOGGER.error('Failed to process account id: %s', str(account_id))
            LOGGER.debug(str(error))
            DATA.session.rollback()

"""
TOKEN
"""
def validate_token(mode=None, token=None):
    LOGGER.info('Validating token for mode: %s', mode)
    return mode == 'subscribe' and token == config.dota2messenger['VALIDATION_TOKEN']

if __name__ == '__main__':
    # initialise_database()
    fill_database()
