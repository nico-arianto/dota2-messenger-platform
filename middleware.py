import dota2api

import config
import logger
from data_access import DataAccess
from middleware_etl import fill_database_detail as fill_database_detail_internal
from middleware_message import received_message as received_message_internal
from middleware_postback import received_postback as received_postback_internal

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
    fill_database_detail_internal(data=DATA, api=API)


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
    received_message_internal(data=DATA, event=event)


"""
Postback
"""


def received_postback(event):
    received_postback_internal(data=DATA, event=event)


if __name__ == '__main__':
    initialise_database()
    fill_database_master()
    fill_database_detail()
