"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
# Little hack to get the parent packages for the bot working in here
import sys
sys.path.append('/opt/project')

import asyncio
import nest_asyncio
import asyncpg
import coc
from datetime import datetime, timedelta
import logging
import traceback

from packages.private.settings import Settings
from packages.logging_setup import BotLogger as LoggerSetup
from packages.cogs.utils.utils import get_utc_monday


SQL_GET_ACTIVE = """SELECT * 
FROM discord_user, clash_account
WHERE is_active = 'true'
  AND discord_user.discord_id = clash_account.discord_id
  AND clash_account.is_primary_account = 'true'"""


SQL_UPDATE_CLASSIC = """INSERT INTO clash_classic_update (increment_date, tag, current_donations, current_trophies, 
                        current_clan_tag, current_clan_name, clash_name, town_hall) VALUES 
                        ($1, $2, $3, $4, $5, $6, $7, $8);"""

SQL_GET_DIFF = """SELECT *
FROM clash_classic_update
WHERE increment_date BETWEEN '{}' AND '{}'
AND tag = '{}' 
ORDER BY increment_date DESC"""

SQL_INSERT_UPDATE_DIFF = """
INSERT INTO clash_classic_update_view
    (week_date, clash_tag, current_donation, current_trophy, current_clan_tag, current_clan_name, clash_name, town_hall) 
VALUES 
    ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT 
    (week_date, clash_tag)
DO UPDATE SET
    current_donation=$3, current_trophy=$4, current_clan_tag=$5, current_clan_name=$6, clash_name=$7, town_hall=$8
"""

SQL_INSERT_CLAN_MEMBERS = "INSERT INTO present_in_clan (clash_tag, player_name, clash_clan_tag) VALUES ($1, $2, $3)"

async def update_in_clan(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.present_in_clan_update')
    try:
        while True:
            log.debug("Updating in-clan roster list")
            members = await coc_client.get_members('#2Y28CGP8')
            in_clan = []
            for member in members:
                in_clan.append((
                    member.tag,
                    member.name,
                    '#2Y28CGP8', # Member.clan doesn't show clan info at this time fix later
                ))
            async with pool.acquire() as conn:
                await conn.execute('DELETE FROM present_in_clan WHERE id > -1')
                await conn.execute("SELECT setval('present_in_clan_id_seq', 1)")
                await conn.executemany(SQL_INSERT_CLAN_MEMBERS, in_clan)

            log.debug(f'Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        log.debug('CTRL + C executed')
    except Exception as error:
        log.critical(error, stack_info=True)

async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.classic_update')

    try:
        while True:
            log.debug("Starting re-occuring update loop")
            # Get all active members
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)

                updates = 0

                async for player in coc_client.get_players((member['clash_tag'] for member in active_members)):
                    if not player:
                        log.error('Was not able to get a player object. We do not have member access')
                        continue
                    try:
                        await conn.execute(SQL_UPDATE_CLASSIC,
                                datetime.utcnow(),
                                player.tag,
                                player.get_achievement("Friend in Need").value,
                                player.trophies,
                                player.clan.tag if player.clan else None,
                                player.clan.name if player.clan else None,
                                player.name,
                                player.town_hall
                        )
                        updates +=1
                    except asyncpg.ForeignKeyViolationError as error:
                        log.error(error, stack_info=True)
                    except Exception as error:
                        log.error(error, stack_info=True)

                log.info(f"Updated {updates} members")
            log.debug(f'Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)

    except KeyboardInterrupt:
        log.debug('CTRL + C executed')
    except Exception as error:
        log.critical(error, stack_info=True)

async def update_weekly_counts(sleep_time: int, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.weekly_update')
    try:
        while True:
            log.debug("Starting weekly update loop")
            start_date = get_utc_monday()
            end_date = get_utc_monday() + timedelta(days=7)
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)
                for member in active_members:
                    member_diffs = await conn.fetch(SQL_GET_DIFF.format(start_date, end_date, member['clash_tag']))
                    if len(member_diffs) == 1:
                        member_diff = dict(member_diffs[0])
                        member_diff['current_donations'] = 0
                        member_diff['current_trophies'] = 0
                        member_diff['clash_name'] = member_diffs[0]['clash_name']
                        member_diff['town_hall'] = member_diffs[0]['town_hall']
                    else:
                        member_diff = dict(member_diffs[0])
                        member_diff['current_donations'] -= member_diffs[-1]['current_donations']
                        member_diff['current_trophies'] -= member_diffs[-1]['current_trophies']

                    await conn.execute(SQL_INSERT_UPDATE_DIFF,
                                   start_date,
                                   member_diff['tag'],
                                   member_diff['current_donations'],
                                   member_diff['current_trophies'],
                                   member_diff['current_clan_tag'],
                                   member_diff['current_clan_name'],
                                   member_diff['clash_name'],
                                   member_diff['town_hall']
                    )
            log.debug(f'Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)
    except KeyboardInterrupt:
        log.debug('CTRL + C executed')
    except Exception as error:
        log.critical(error, stack_info=True)
        exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
        print(exc)


async def main(coc_client_):
    """Async start point will for all background tasks"""
    LoggerSetup(SETTINGS, 'PantherDaemon')
    log = logging.getLogger('PantherDaemon')
    log.debug("Starting background loops")
    pool : asyncpg.pool.Pool = await asyncpg.create_pool(SETTINGS.dsn)
    loop = asyncio.get_running_loop()

    tasks = [
        loop.create_task(update_active_users(300, coc_client_, pool)),
        loop.create_task(update_weekly_counts(300, pool)),
        loop.create_task(update_in_clan(300, coc_client_, pool))
    ]
    await asyncio.wait(tasks)


if __name__ == '__main__':
    SETTINGS = Settings(daemon=True)

    # Nest patches asyncio to allow for nested loops to allow logging into coc
    nest_asyncio.apply()

    _coc_client: coc.client.Client = coc.login(
        SETTINGS.coc_user,
        SETTINGS.coc_pass,
        key_names="Panther Daemon",
    )
    asyncio.run(main(_coc_client))