from facebook2api import send_text_message
from facebook2api import send_generic_message
import logger

LOGGER = logger.getLogger(__name__)

STATISTIC_CODE = 'S'
HEROES_CODE = 'H'
ITEM_CODE = 'I'

"""
User defined payload
"""
def create_payload(command, account_id):
    return command + ' ' + str(account_id)

def _get_command(payload):
    return payload[0:1]

def _get_account_id(payload):
    account_id_text = payload[2:]
    try:
        return int(account_id_text)
    except ValueError as error:
        LOGGER.error('Failed to converted %s to an int, error: %s', account_id_text, str(error))
    return

"""
Postback
"""
def received_postback(data, event):
    sender_id = event['sender']['id']
    recipient_id = event['recipient']['id']
    time_of_postback = event['timestamp']
    payload = event['postback']['payload']
    command = _get_command(payload=payload)
    account_id = _get_account_id(payload=payload)
    if command and account_id:
        if command == STATISTIC_CODE:
            _send_statistic_message(recipient_id=sender_id, account_id=account_id)
        elif command == HEROES_CODE:
            _send_heroes_message(recipient_id=sender_id, account_id=account_id)
        elif command == ITEM_CODE:
            _send_items_message(recipient_id=sender_id, account_id=account_id)
        else:
            LOGGER.error('Unknown payload command %s', command)
        return
    LOGGER.error('Corrupted payload %s', payload)

def _generate_statistic_message(matches, win_rate):
    return 'Matches: {:d} Win Rate: {:.2f} %'.format(matches, win_rate)

def _send_statistic_message(recipient_id, account_id):
    matches = 0
    win_rate = 0
    match_summary = data.get_match_summary(account_id=account_id)
    if match_summary:
        matches = match_summary.matches
        win_rate = match_summary.win_rate
    send_text_message(recipient_id=recipient_id, message_text=_generate_statistic_message(matches=matches, win_rate=win_rate))

def _send_heroes_message(recipient_id, account_id):
    elements = []
    match_hero_summaries = data.get_math_hero_summary(account_id=account_id)
    for match_hero_summary in match_hero_summaries:
        hero = match_hero_summary.hero
        elements.append({
            'title': hero.hero_name,
            'subtitle': _generate_statistic_message(matches=match_hero_summary.matches, win_rate=match_hero_summary.win_rate),
            'image_url': hero.portrait_url
        })
    send_generic_message(recipient_id=recipient_id, elements=elements)

def _send_items_message(recipient_id, account_id):
    elements = []
    match_item_summaries = data.get_match_item_summary(account_id=account_id)
    for match_item_summary in match_item_summaries:
        item = match_item_summary.item
        elements.append({
            'title': item.item_name,
            'subtitle': _generate_statistic_message(matches=match_item_summary.matches, win_rate=match_item_summary.win_rate),
            'image_url': item.image_url
        })
    send_generic_message(recipient_id=recipient_id, elements=elements)
