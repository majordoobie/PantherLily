from datetime import datetime

from discord.ext import commands
import logging

from bot import BotClient

from packages.cogs.utils.bot_sql import *
from packages.cogs.utils.utils import *


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.leaders')

    async def _get_updates(self, member_id: int) -> tuple:
        """Method gets the most up to date user information - this code is repeated a lot in this class"""
        async with self.bot.pool.acquire() as con:
            db_discord_member = await con.fetchrow(sql_select_discord_user_id(), member_id)
            db_clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member_id)
        return db_discord_member, db_clash_accounts


    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `add_user` command args: `{arg_string}`')

        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
                'required': True,
                'type': 'int'
            },
            'coc_alternate': {
                'flags': ['--set-alternate'],
                'switch': True,
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return

        # Get user objects
        player = await get_coc_player(ctx, args['coc_tag'], self.bot.coc_client, self.bot.embed_print)
        member = await get_discord_member(ctx, args['discord_id'], self.bot.embed_print)
        if not player or not member:
            return

        discord_record = (
            member.id,
            member.name,
            member.display_name,
            member.discriminator,
            member.joined_at,
            member.created_at,
            datetime.utcnow(),
        )
        coc_record = (
            player.tag,
            member.id,
        )

        async with self.bot.pool.acquire() as con:
            db_discord_member, db_clash_accounts = await self._get_updates(member.id)

            # Add a brand new user that is not in the database at all
            if db_discord_member is None and len(db_clash_accounts) == 0:
                self.log.debug(f'Adding new user {member.name} with clash of {player.tag}')
                await con.execute(sql_insert_discord_user(), *discord_record)
                await con.execute(sql_insert_clash_account(), *coc_record)
                db_discord_member, db_clash_accounts = await self._get_updates(member.id)

                msg = account_panel(db_discord_member, db_clash_accounts, "New user added")
                await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(), ctx.author.id, msg)
                self.log.info(msg)
                await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)


            # If user HAS a discord account BUT their active state is set to false
            elif db_discord_member['is_active'] == False:
                self.log.debug(f'Discord member `{member.name}:{member.id}` already exits, but `is_active` attribute is '
                              f'set to `false`')

                # If they have 0 clash accounts then their main account was probably removed so just add one and move on
                if len(db_clash_accounts) == 0:
                    await con.execute(sql_update_discord_user_is_active(), True, member.id)
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                    msg = account_panel(db_discord_member, db_clash_accounts, "User enabled")
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                    await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(), ctx.author.name, msg)

                # If they have one account - then we need to see if the clash tag they are adding is the same
                elif len(db_clash_accounts) == 1:
                    # If the clash tag arg is the same that is in the database then we are just enabling their account
                    if db_clash_accounts[0]['clash_tag'] == player.tag:
                        await con.execute(sql_update_discord_user_is_active(), True, member.id)
                        await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                        db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                        msg = account_panel(db_discord_member, db_clash_accounts, "User enabled")
                        self.log.info(msg)
                        await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                        await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                          ctx.author.name, msg)

                    # If the clash arg that they are using does not match then look for the coc_alternate flag in the
                    # command if it's not there then fail out and tell them
                    else:
                        #TODO: finish combining set-alternate
                        if not args['coc_alternate']:
                            title = f'User already has a clash account. If you would like to add another please use' \
                                    f'the following command\n\n{arg_string} --set-alternate'
                            msg = account_panel(db_discord_member, db_clash_accounts, title)
                            self.log.warning(msg)
                            await self.bot.embed_print(ctx, msg, title='Multiple clash accounts', color=self.bot.WARNING)
                            return
                        # if the user added the flag then add the new clash account and set it to primary
                        else:
                            await con.execute(sql_update_discord_user_is_active(), True, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                            await con.execute(sql_insert_clash_account(), *coc_record)
                            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                            msg = account_panel(db_discord_member, db_clash_accounts)
                            self.log.info('New clash account added\n'+msg)
                            await self.bot.embed_print(ctx, msg, title='New clash account added', color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                              ctx.author.name, msg)
                            return

                else:
                    for clash_account in db_clash_accounts:
                        if clash_account['clash_tag'] == player.tag:
                            await con.execute(sql_update_discord_user_is_active(), True, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                            msg = f'Set discord user {member.name}:{member.id} `is_active` attribute to `True` with clash account ' \
                                  f'`{player.tag}` as the primary account\n{account_panel(db_discord_member, clash_accounts)}'
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg)
                            return

            elif db_discord_member['is_active']:
                if len(db_clash_accounts) == 0:
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    msg = f'Discord user `{member.name}:{member.id}` already exits and `is_active` attribute is set ' \
                          f'to `True`. Adding clash account `{player.tag}`'
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg)
                    return

                elif len(db_clash_accounts) == 1:
                    if db_clash_accounts[0]['clash_tag'] == player.tag:
                        if db_clash_accounts[0]['is_primary_account']:
                            msg = f'Discord member `{member.name}:{member.id}` is already active with the clash account ' \
                                  f'of `{player.tag}`; skipping...'
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg)
                            return
                        else:
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                            msg = f'Modified user coc primary account\n{account_panel(db_discord_member, clash_accounts)}'
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg)

                    else:
                        if not args['coc_alternate']:
                            msg = alternate_account(db_discord_member, db_clash_accounts, args)
                            self.log.warning(msg)
                            await self.bot.embed_print(ctx, msg, color=self.bot.WARNING)
                            return

                        else:
                            await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                            await con.execute(sql_insert_clash_account(), *coc_record)
                            clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                            acc_panel = account_panel(db_discord_member, clash_accounts)
                            msg = f'Added alternate account to `{member.name}`\n' \
                                  f'\nSet `{player.tag} -> Primary`\n\n{acc_panel}'
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg)

                else:
                    for coc_account in db_clash_accounts:
                        if coc_account["clash_tag"] == player.tag:
                            if coc_account["is_primary_account"]:
                                await self.bot.embed_print(ctx, f"Clash account is already primary\n{account_panel(db_discord_member, db_clash_accounts)}")
                            else:
                                if not args['coc_alternate']:
                                    msg = f'Discord member `{member.name}:{member.id}` already has a clash account of ' \
                                          f'`{player.tag}` if you would like to add another clash account please use the following ' \
                                          f'command:\n\n `{arg_string} --set-alternate`'
                                    self.log.warning(msg)
                                    await self.bot.embed_print(ctx, msg, color=self.bot.WARNING)
                                    return
                                else:
                                    await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                                    await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                                    db_clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                                    msg = f'`{player.tag}` is now the primary account for {member.name}\n{account_panel(db_discord_member, db_clash_accounts)}'
                                    self.log.info(msg)
                                    await self.bot.embed_print(ctx, msg)



    @commands.check(is_leader)
    @commands.command(aliases=['delete-coc-link', 'delete_coc_link'])
    async def del_coc(self, ctx, *, arg_string=None):
        self.log.debug(f'User: `{ctx.author}` is running `del_coc` command args: `{arg_string}`')

        arg_dict = {
            'coc_tag': {
                'flags': ['--clash', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord', '-d'],
                'required': True,
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        if not args:
            return

        player = await get_coc_player(ctx, args['coc_tag'], self.bot.coc_client, self.bot.embed_print)
        member = await get_discord_member(ctx, args['discord_id'], self.bot.embed_print)
        if not player or not member:
            return

        async with self.bot.pool.acquire() as con:
            discord_member = await con.fetchrow(sql_select_discord_user_id(), member.id)
            clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
            for clash_account in clash_accounts:
                if clash_account['clash_tag'] == player.tag:
                    await con.execute(sql_delete_clash_account_record(), player.tag, member.id)
                    clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                    msg = f'Removed `{player.tag}` from `{member.name}:{member.id}`\n{account_panel(discord_member, clash_accounts)}'
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg)
                    return
            await self.bot.embed_print(ctx, f"Nothing to delete, check commands\n{account_panel(discord_member, clash_accounts)}")

def account_panel(discord_member: dict, coc_accounts: list, title: str='') -> str:
    coc_panel = f'`{"Clash Tag":<15}` `{"Primary Acc":<15}`\n'
    for coc_account in coc_accounts:
        coc_bool = "True" if coc_account['is_primary_account'] else "False"
        coc_panel += f'`{coc_account["clash_tag"]:<15}` `{coc_bool:<15}`\n'

    if coc_panel == '':
        coc_panel = "No CoC Accounts Bound"

    base = f'__Player Account__\n' \
           f'`{"Discord Name:":<14}` `{discord_member["discord_nickname"]}`\n' \
           f'`{"Is Active:":<14}` `{discord_member["is_active"]}`\n' \
           f'\n__Clash Accounts__:\n' \
           f'{coc_panel}'

    if title == '':
        return base
    else:
        return f'{title}\n\n{base}'

def alternate_account(discord_member: dict, coc_accounts: list, args) -> str:
    arg_string = f'-d {args["discord_id"]}\n-c {args["coc_tag"]}\n--set-alternate'
    title = f'User `{discord_member["discord_name"]}` already has a clash account. If you would like to set an ' \
            f'alternate then please use the following command:\n\n`{arg_string}`'
    return account_panel(discord_member, coc_accounts, title)




def setup(bot):
    bot.add_cog(Leaders(bot))


