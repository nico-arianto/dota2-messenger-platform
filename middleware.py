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
Master
"""
def fill_database_master():

    # Heroes
    heroes = API.get_heroes()
    if heroes is None:
        return
    for hero in heroes['heroes']:
        hero_id = hero['id']
        hero_name = hero['localized_name']
        portrait_url = hero['url_full_portrait']
        data_hero = DATA.get_hero(hero_id=hero_id)
        if data_hero:
            data_hero.hero_name = hero_name
            data_hero.portrait_url = portrait_url
            DATA.update_hero(hero=data_hero)
            LOGGER.info('Updated hero id: %d', hero_id)
        else:
            DATA.add_hero(hero_id=hero_id,
                          hero_name=hero_name,
                          portrait_url=portrait_url)
            LOGGER.info('Created hero id: %d', hero_id)

    # Items
    items = API.get_game_items()
    if items is None:
        return
    for item in items['items']:
        item_id = item['id']
        item_name = item['localized_name']
        image_url = item['url_image']
        data_item = DATA.get_item(item_id=item_id)
        if data_item:
            data_item.item_name = item_name
            data_item.image_url = image_url
            DATA.update_item(data_item)
            LOGGER.info('Updated item id: %d', item_id)
        else:
            DATA.add_item(item_id=item_id,
                          item_name=item_name,
                          image_url=image_url)
            LOGGER.info('Created item id: %d', item_id)

"""
ETL
"""
def fill_database_detail():

    # Retrieving the last match id
    last_history = DATA.get_last_history()
    start_at_match_seq_num = None
    if last_history:
        start_at_match_seq_num = last_history.last_match_id
    LOGGER.info('ETL start from math id: %s', str(start_at_match_seq_num))

    # Looping the next 100 matches history
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

    # Records the last match id in the history
    DATA.add_history(last_match_id=last_match)
    LOGGER.info('ETL finish with math id: %d', last_match)

def __fill_player(account_id):
    LOGGER.info('Find account id: %d', account_id)
    # Important: Cannot utilize steamids with account_ids, because the orders of returned players was not in the same sequence and no account id in the response.
    players = API.get_player_summaries(steamids=account_id)
    if players is None:
        LOGGER.info('Not found account id: %d', account_id)
        return
    for player in players['players']:
        steam_id = player['steamid']
        real_name = player.get('realname', None)
        persona_name = player.get('personaname', None)
        avatar = player.get('avatarfull', None)
        profile_url = player.get('profileurl', None)
        data_player = DATA.get_player(account_id=account_id)
        try:
            if data_player:
                data_player.steam_id = steam_id
                data_player.real_name = real_name
                data_player.persona_name = persona_name
                data_player.avatar = avatar
                data_player.profile_url = profile_url
                DATA.update_player(player=data_player)
                LOGGER.info('Updated account id: %d', account_id)
            else:
                DATA.add_player(account_id=account_id,
                                steam_id=steam_id,
                                profile_url=profile_url,
                                real_name=real_name,
                                persona_name=persona_name,
                                avatar=avatar)
                LOGGER.info('Created account id: %d', account_id)

        except DatabaseError as error: # TODO: Temporary ignore the unsupported data, especially the unicode issue.
            LOGGER.error('Failed to process account id: %d, error: %s', account_id, str(error))
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
    message_value = _get_value(message_text, 'find')
    if message_value:
        try:
            player_id = int(message_value)
            player = DATA.get_player(account_id=player_id)
            if player is None:
                player = DATA.get_player(steam_id=player_id)
            if player:
                _send_players_message(recipient_id, [ player ])
            else:
                send_text_message(recipient_id, 'No player with that id was found')
        except ValueError as error:
            LOGGER.error('Failed to converted %s to an int, error: %s', message_value, str(error))
        return

    # search players by name
    message_value = _get_value(message_text, 'search')
    if message_value:
        player_name = message_value
        players = DATA.get_player(real_name=player_name)
        if players and len(players) > 0:
            _send_players_message(recipient_id, players)
        else:
            send_text_message(recipient_id, 'No player with that name was found')
        return

    send_text_message(recipient_id, 'To start the look up of Dota2 players, please type "find <player_id>" or "search <player_name>"')

def _get_value(text, command):
    index = text.find(command)
    if index > -1:
        value = text[index + len(command):].strip()
        if value:
            return value
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
    fill_database_master()
    fill_database_detail()
