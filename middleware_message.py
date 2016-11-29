from facebook2api import send_text_message
from facebook2api import send_generic_message
from middleware_postback import STATISTIC_CODE
from middleware_postback import HEROES_CODE
from middleware_postback import ITEM_CODE
from middleware_postback import create_payload
import logger

LOGGER = logger.getLogger(__name__)

FIND_COMMAND = 'find'
SEARCH_COMMAND = 'search'
PLAYERS_COMMAND = 'players'

"""
Message
"""
def received_message(data, event):
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
        send_text_message(recipient_id=sender_id, message_text='Quick reply tapped')
        return

    if message_text:
        _process_text_message(data=data, recipient_id=sender_id, message_text=message_text)
    elif message_attachments:
        send_text_message(recipient_id=sender_id, message_text='Message with attachments received')

def _process_text_message(data, recipient_id, message_text):

    # find top players
    if message_text == PLAYERS_COMMAND:
        _process_players(data=data, recipient_id=recipient_id)
        return

    # find player by id
    message_value = _get_value(text=message_text, command=FIND_COMMAND)
    if message_value:
        try:
            player_id = int(message_value)
            _process_player_by_id(data=data, recipient_id=recipient_id, player_id=player_id)
        except ValueError as error:
            LOGGER.error('Failed to converted %s to an int, error: %s', message_value, str(error))
        return

    # search players by name
    message_value = _get_value(text=message_text, command=SEARCH_COMMAND)
    if message_value:
        player_name = message_value
        _process_players_by_name(data=data, recipient_id=recipient_id, player_name=player_name)
        return

    send_text_message(recipient_id=recipient_id, message_text='To start the look up of Dota2 players, please type:\n\n "{} <player_id>"\n   or\n "{} <player_name>"\n   or\n "{}"'.format(FIND_COMMAND, SEARCH_COMMAND, PLAYERS_COMMAND))

def _process_players(data, recipient_id):
    match_summaries = data.get_top_player()
    if match_summaries and len(match_summaries) > 0:
        players = []
        for match_summary in match_summaries:
            players.append(match_summary.player)
        _send_players_message(recipient_id=recipient_id, players=players)
    else:
        send_text_message(recipient_id=recipient_id, message_text='No player was found')

def _process_player_by_id(data, recipient_id, player_id):
    player = data.get_player(account_id=player_id)
    if player is None:
        player = data.get_player(steam_id=player_id)
    if player:
        _send_players_message(recipient_id=recipient_id, players=[ player ])
    else:
        send_text_message(recipient_id=recipient_id, message_text='No player with that id was found')

def _process_players_by_name(data, recipient_id, player_name):
    players = data.get_player(real_name=player_name)
    if players and len(players) > 0:
        _send_players_message(recipient_id=recipient_id, players=players)
    else:
        send_text_message(recipient_id=recipient_id, message_text='No player with that name was found')

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
                'title': 'Stats',
                'payload': create_payload(command=STATISTIC_CODE, account_id=player.account_id)
            }, {
                'type': 'postback',
                'title': 'Top 10 Heroes',
                'payload': create_payload(command=HEROES_CODE, account_id=player.account_id)
            }, {
                'type': 'postback',
                'title': 'Top 10 Items',
                'payload': create_payload(command=ITEM_CODE, account_id=player.account_id)
            }]
        })
    send_generic_message(recipient_id=recipient_id, elements=elements)
