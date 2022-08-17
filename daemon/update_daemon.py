"""
This service will be used to automatically update the database with fresh information away from the bot to avoid
any slowdowns from I/O.
"""
# Little hack to get the parent packages for the bot working in here
import sys
from pathlib import Path


import asyncio
import asyncpg
import coc
from datetime import datetime, timedelta
import logging
import traceback

from packages.private.settings import Settings
from packages.logging_setup import BotLogger as LoggerSetup
from packages.utils.utils import get_utc_monday

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
    (week_date, clash_tag, donation_gains, trophy_diff, current_clan_tag, current_clan_name, clash_name, town_hall, 
    fin_value, current_trophy) 
VALUES 
    ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10)
ON CONFLICT 
    (week_date, clash_tag)
DO UPDATE SET
    donation_gains=$3, trophy_diff=$4, current_clan_tag=$5, current_clan_name=$6, clash_name=$7, town_hall=$8,
    fin_value=$9, current_trophy=$10
"""

SQL_INSERT_CLAN_MEMBERS = "INSERT INTO present_in_clan (clash_tag, player_name, clash_clan_tag) VALUES ($1, $2, $3)"


async def update_in_clan(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.present_in_clan_update')
    while True:
        try:
            log.debug("[CLAN UPDATE] Updating in-clan roster list")
            members = await coc_client.get_members('#2Y28CGP8')
            in_clan = []
            for member in members:
                in_clan.append((
                    member.tag,
                    member.name,
                    '#2Y28CGP8',  # Member.clan doesn't show clan info at this time fix later
                ))
            async with pool.acquire() as conn:
                await conn.execute('DELETE FROM present_in_clan WHERE id > -1')
                await conn.execute("SELECT setval('present_in_clan_id_seq', 1)")
                await conn.executemany(SQL_INSERT_CLAN_MEMBERS, in_clan)

            log.debug(f'[CLAN UPDATE] Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            log.debug('CTRL + C executed')
        except Exception as error:
            log.critical(error, exc_info=True)
            log.debug('[CLAN UPDATE] Attempting to continue working...')
            await asyncio.sleep(sleep_time)


async def update_active_users(sleep_time: int, coc_client: coc.client.Client, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.classic_update')
    while True:
        try:
            log.debug("[ACTIVE UPDATE] Starting re-occuring update loop")
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)

                updates = 0

                async for player in coc_client.get_players((member['clash_tag'] for member in active_members)):
                    if not player:
                        log.error('[CLAN UPDATE] Was not able to get a player object. We do not have member access')
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
                        updates += 1
                    except asyncpg.ForeignKeyViolationError as error:
                        log.error(error, exc_info=True)
                    except Exception as error:
                        log.error(error, exc_info=True)

                log.info(f"[CLAN UPDATE] Updated {updates} members")
            log.debug(f'[CLAN UPDATE] Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)

        except KeyboardInterrupt:
            log.debug('CTRL + C executed')
        except Exception as error:
            log.critical(error, exc_info=True)
            log.debug('[CLAN UPDATE] Attempting to continue working...')
            await asyncio.sleep(sleep_time)


async def update_weekly_counts(sleep_time: int, pool: asyncpg.pool.Pool):
    log = logging.getLogger('PantherDaemon.weekly_update')
    while True:
        try:
            log.debug("[WEEKLY SYNC] Starting weekly update loop")
            start_date = get_utc_monday()
            end_date = get_utc_monday() + timedelta(days=7)
            async with pool.acquire() as conn:
                active_members = await conn.fetch(SQL_GET_ACTIVE)
                for member in active_members:
                    member_diffs = await conn.fetch(SQL_GET_DIFF.format(start_date, end_date, member['clash_tag']))
                    # If there is no difference then just continue to the commit
                    if not member_diffs:
                        continue
                    
                    if len(member_diffs) == 1:
                        member_diff = dict(member_diffs[0])
                        member_diff['donation_gains'] = 0
                        member_diff['trophy_diff'] = 0
                        member_diff['clash_name'] = member_diffs[0]['clash_name']
                        member_diff['town_hall'] = member_diffs[0]['town_hall']
                    else:
                        member_diff = dict(member_diffs[0])
                        member_diff['donation_gains'] = member_diff['current_donations'] - member_diffs[-1][
                            'current_donations']
                        member_diff['trophy_diff'] = member_diff['current_trophies'] - member_diffs[-1][
                            'current_trophies']

                    await conn.execute(
                        SQL_INSERT_UPDATE_DIFF,
                        start_date,
                        member_diff['tag'],
                        member_diff['donation_gains'],
                        member_diff['trophy_diff'],
                        member_diff['current_clan_tag'],
                        member_diff['current_clan_name'],
                        member_diff['clash_name'],
                        member_diff['town_hall'],
                        member_diff['current_donations'],
                        member_diff['current_trophies']
                    )
            log.debug(f'[WEEKLY SYNC] Sleeping for {sleep_time} seconds')
            await asyncio.sleep(sleep_time)
        except KeyboardInterrupt:
            log.debug('[WEEKLY SYNC] CTRL + C executed')
        except Exception as error:
            log.critical(error, exc_info=True)
            exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
            print(exc)
            await asyncio.sleep(sleep_time)

def _get_coc_client(settings: Settings) -> coc.Client:
    """
    Init the Client class with custom settings

    :param settings: configuration for the bot
    :type settings: settings
    :return: Configured Client class
    """
    return coc.Client(
        key_count=4,
        throttler_limit=30,
        client=coc.EventsClient,
        key_names=settings.bot_config["key_name"],
    )


async def main():
    """Async start point will for all background tasks"""
    project_path = Path.cwd().resolve().parent
    sys.path.append(project_path.as_posix())
    settings = Settings(project_path, "live_mode", daemon=True)

    LoggerSetup(settings)

    log = logging.getLogger('PantherDaemon')
    log.debug("['DAEMON ROOT] Starting background loops")
    pool: asyncpg.pool.Pool = await asyncpg.create_pool(settings.dsn)
    loop = asyncio.get_running_loop()

    coc_client = _get_coc_client(settings)
    await coc_client.login(settings.coc_user, settings.coc_pass)

    tasks = [
        loop.create_task(update_active_users(300, coc_client, pool)),
        loop.create_task(update_weekly_counts(300, pool)),
        loop.create_task(update_in_clan(300, coc_client, pool))
    ]
    await asyncio.wait(tasks)


if __name__ == '__main__':

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
