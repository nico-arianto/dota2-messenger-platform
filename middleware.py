import dota2api
from sqlalchemy.exc import DatabaseError

from data_access import DataAccess
from facebook2api import send_text_message
from facebook2api import send_generic_message
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
        avatar = player.get('avatarmedium', None)
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

"""
Message
"""
def received_message(event):
    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    time_of_message = event['timestamp']
    message = event['message']

    LOGGER.info('Received message for user %s and page %s at %d with message: %s', sender_id, recipient_id, time_of_message, message)

    is_echo = message.get('is_echo', None)
    message_id = message.get('mid', None)
    app_id = message.get('app_id', None)
    metadata = message.get('metadata', None)
    message_text = message.get('text', None)
    message_attachments = message.get('attachments', None)
    quick_reply = message.get('quick_reply', None)

    if is_echo:
        LOGGER.info('Received echo for message id %s and app id %d with metadata %s', message_id, app_id, metadata)
        return
    elif quick_reply:
        LOGGER.info('Quick reply for message id %s', message_id)
        send_text_message(sender_id, 'Quick reply tapped')
        return

    if message_text:
        _process_text_message(sender_id, message_text)
    elif message_attachments:
        send_text_message(sender_id, 'Message with attachments received')

def _process_text_message(recipient_id, message_text):

    # find player by id
    message_value = _get_message_value(message_text, 'find')
    if message_value:
        player_id = int(message_value)
        player = DATA.get_player(account_id=player_id)
        if player is None:
            player = DATA.get_player(steam_id=player_id)
        if player:
            _send_players_message(recipient_id, [ player ])
        else:
            send_text_message(recipient_id, 'No player with that id was found')
        return

    # search players by name
    message_value = _get_message_value(message_text, 'search')
    if message_value:
        player_name = message_value
        players = DATA.get_player(real_name=player_name)
        if players and len(players) > 0:
            _send_players_message(recipient_id, players)
        else:
            send_text_message(recipient_id, 'No player with that name was found')
        return

    send_text_message(recipient_id, 'To start the look up of Dota2 players, please type "find <player_id>" or "search <player_name>"')

def _get_message_value(message_text, message_command):
    index = message_text.find(message_command)
    if index > -1:
        message_value = message_text[index + len(message_command):].strip()
        if message_value:
            return message_value
    return

def _send_players_message(recipient_id, players):
    elements = []
    for player in players:
        elements.append({
            'title': player.persona_name,
            'subtitle': player.real_name,
            'item_url': player.profile_url,
            'image_url': player.avatar,
            'buttons': [{
                'type': 'postback',
                'title': 'Statistics',
                'payload': 'S ' + str(player.account_id)
            }, {
                'type': 'postback',
                'title': 'Heroes',
                'payload': 'H ' + str(player.account_id)
            }, {
                'type': 'postback',
                'title': 'Items',
                'payload': 'I ' + str(player.account_id)
            }]
        })
    send_generic_message(recipient_id, elements)

if __name__ == '__main__':
    initialise_database()
    fill_database()
