from dota2api.src.exceptions import APIError
from dota2api.src.exceptions import APITimeoutError
from sqlalchemy.exc import DatabaseError

import logger

LOGGER = logger.getLogger(__name__)


def fill_database_detail(data, api):
    # Retrieving the last match id
    last_history = data.get_last_history()
    start_match_id = last_history.last_match_id + 1 if last_history else 0
    LOGGER.info('ETL start from math id: %d', start_match_id)

    # Looping the next 100 matches history
    next_match_history = api.get_match_history_by_seq_num(start_at_match_seq_num=start_match_id)
    if next_match_history is None:
        return
    elif next_match_history['status'] != 1:
        raise ValueError(next_match_history['statusDetail'])
    account_ids = []
    invalid_account_ids = []
    last_match_id = start_match_id
    for match in next_match_history['matches']:
        match_id = match['match_id']
        last_match_id = match_id
        radiant_win = match['radiant_win']
        for player in match['players']:
            if 'account_id' not in player:
                continue
            account_id = player['account_id']
            if account_id in invalid_account_ids:
                continue
            if account_id not in account_ids:
                if not __fill_player(data=data, api=api, account_id=account_id):
                    invalid_account_ids.append(account_id)
                    continue
                account_ids.append(account_id)

            # Records the match
            player_slot = player['player_slot']
            player_win = True if player_slot < 5 and radiant_win else False
            hero_id = player['hero_id']
            data.add_match_hero(match_id=match_id,
                                account_id=account_id,
                                player_win=player_win,
                                hero_id=hero_id)
            LOGGER.info('Created match id: %d with hero id: %d', match_id, hero_id)
            item_ids = []
            for index in range(0, 6):
                item_id = player['item_' + str(index)]
                if item_id > 0 and item_id not in item_ids:
                    data.add_match_item(match_id=match_id,
                                        account_id=account_id,
                                        player_win=player_win,
                                        item_id=item_id)
                    LOGGER.info('Created match id: %d with item id: %d', match_id, item_id)
                    item_ids.append(item_id)

    if start_match_id != last_match_id:
        _summarize_match(data=data, start_match_id=start_match_id)

        # Records the last match id in the history
        data.add_history(last_match_id=last_match_id)
    LOGGER.info('ETL finish with math id: %d', last_match_id)


def __fill_player(data, api, account_id):
    LOGGER.info('Find account id: %d', account_id)
    # Important: Cannot utilize steamids with account_ids, because the orders of returned players was not in the same sequence and no account id in the response.
    try:
        players = api.get_player_summaries(steamids=account_id)
    except (APIError, APITimeoutError):
        # Temporary creates a blank account with consideration that this account will be synch up again in the next fill_database_detail() invocation.
        players = {
            'players': [
                {
                    'steamid': account_id,
                    'profileurl': 'N/A'
                }
            ]
        }
    if players is None:
        LOGGER.info('Not found account id: %d', account_id)
        return False
    for player in players['players']:
        steam_id = player['steamid']
        real_name = player.get('realname', None)
        persona_name = player.get('personaname', None)
        avatar = player.get('avatarfull', None)
        profile_url = player.get('profileurl', None)
        data_player = data.get_player(account_id=account_id)
        try:
            if data_player:
                data_player.steam_id = steam_id
                data_player.real_name = real_name
                data_player.persona_name = persona_name
                data_player.avatar = avatar
                data_player.profile_url = profile_url
                data.update_player(player=data_player)
                LOGGER.info('Updated account id: %d', account_id)
            else:
                data.add_player(account_id=account_id,
                                steam_id=steam_id,
                                profile_url=profile_url,
                                real_name=real_name,
                                persona_name=persona_name,
                                avatar=avatar)
                LOGGER.info('Created account id: %d', account_id)
            return True
        except DatabaseError as error:  # Temporary ignore the unsupported data, especially the unicode issue.
            LOGGER.error('Failed to process account id: %d, error: %s', account_id, str(error))
            data.session.rollback()
    return False


def _summarize_match(data, start_match_id):
    match_summaries = data.get_match_summary_aggregate(match_id=start_match_id)
    for match_summary in match_summaries:
        data.save_match_summary(account_id=match_summary.account_id,
                                player_win=match_summary.player_win,
                                matches=match_summary.matches)
        LOGGER.info('Summarize account id: %d', match_summary.account_id)
    match_hero_summaries = data.get_match_hero_summary_aggregate(match_id=start_match_id)
    for match_hero_summary in match_hero_summaries:
        data.save_match_hero_summary(account_id=match_hero_summary.account_id,
                                     hero_id=match_hero_summary.hero_id,
                                     player_win=match_hero_summary.player_win,
                                     matches=match_hero_summary.matches)
        LOGGER.info('Summarize account id: %d and hero id: %d', match_hero_summary.account_id,
                    match_hero_summary.hero_id)
    match_item_summaries = data.get_match_item_summary_aggregate(match_id=start_match_id)
    for match_item_summary in match_item_summaries:
        data.save_match_item_summary(account_id=match_item_summary.account_id,
                                     item_id=match_item_summary.item_id,
                                     player_win=match_item_summary.player_win,
                                     matches=match_item_summary.matches)
        LOGGER.info('Summarize account id: %d and item id: %d', match_item_summary.account_id,
                    match_item_summary.item_id)
