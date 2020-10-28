import traceback
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

    async def _multi_account_logic(self, ctx, coc_record, member, player, args):
        """Repeated code in add_user"""
        async with self.bot.pool.acquire() as con:
            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
            if not args['coc_alternate']:
                msg = alternate_account(db_discord_member, db_clash_accounts, args)
                self.log.warning(msg)
                await self.bot.embed_print(ctx, msg, title='Multiple clash accounts', color=self.bot.WARNING)
                # if the user added the flag then add the new clash account and set it to primary
            else:
                await con.execute(sql_update_discord_user_is_active(), True, member.id)
                await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                await con.execute(sql_insert_clash_account(), *coc_record)
                db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                msg = account_panel(db_discord_member, db_clash_accounts, "Alternate clash account set")
                self.log.info(msg)
                await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                              ctx.author.id, msg)

    async def _set_defaults(self, ctx, member, clash_level: int, in_game_name: str):
        """Set default roles and name change"""
        if clash_level == 11:
            clash_level_role = self.bot.settings.default_roles['th11s']
        elif clash_level == 12:
            clash_level_role = self.bot.settings.default_roles['th12s']
        elif clash_level == 13:
            clash_level_role = self.bot.settings.default_roles['th13s']
        else:
            raise IndexError(f"No TH role found for level {clash_level}")

        clash_level_role = ctx.guild.get_role(clash_level_role)
        coc_member_role = self.bot.settings.default_roles['CoC Members']
        coc_member_role = ctx.guild.get_role(coc_member_role)

        if clash_level_role is None or coc_member_role is None:
            if clash_level_role:
                raise discord.InvalidData(f'Unable to retrieve role for Town Hall {clash_level}')
            else:
                raise discord.InvalidData(f'Unable to retrieve role for CoC Members')

        try:
            await member.add_roles(coc_member_role)
            self.bot.log_role_change(member, coc_member_role)
            await member.add_roles(clash_level_role)
            self.bot.log_role_change(member, clash_level_role)
        except Exception as error:
            self.bot.log.error(error, exc_info=True)
            exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
            await self.bot.embed_print(ctx, exc, title='User role change error', color=self.bot.ERROR)

        try:
            await member.edit(nick=in_game_name, reason='Panther Bot')
            self.log.debug(f'Changed {member.name} name to {member.nick}')
        except Exception as error:
            self.bot.log.error(error, exc_info=True)
            exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
            await self.bot.embed_print(ctx, exc, title='Unable to change users nickname', color=self.bot.ERROR)





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
                    await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(), ctx.author.id, msg)

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
                                          ctx.author.id, msg)

                    # If the clash arg that they are using does not match then look for the coc_alternate flag in the
                    # command if it's not there then fail out and tell them
                    else:
                        await self._multi_account_logic(ctx, coc_record, member, player, args)

                elif len(db_clash_accounts) > 1:
                    for clash_account in db_clash_accounts:
                        if clash_account['clash_tag'] == player.tag:
                            await con.execute(sql_update_discord_user_is_active(), True, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                            msg = account_panel(db_discord_member, db_clash_accounts, 'User enabled')
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                              ctx.author.id, msg)
                            await self._set_defaults(ctx, member, player.town_hall, player.name)
                            return

                    await self._multi_account_logic(ctx, coc_record, member, player, args)


            elif db_discord_member['is_active']:
                if len(db_clash_accounts) == 0:
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                    msg = account_panel(db_discord_member, db_clash_accounts, 'Clash account assigned')
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                    await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                  ctx.author.id, msg)

                elif len(db_clash_accounts) == 1:
                    if db_clash_accounts[0]['clash_tag'] == player.tag:
                        if db_clash_accounts[0]['is_primary_account']:
                            msg = account_panel(db_discord_member, db_clash_accounts, 'No action taken')
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg)

                        else:
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                            msg = account_panel(db_discord_member, db_clash_accounts, 'Clash account set')
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                      ctx.author.id, msg)
                    else:
                        await self._multi_account_logic(ctx, coc_record, member, player, args)

                elif len(db_clash_accounts) > 1:
                    for clash_account in db_clash_accounts:
                        if clash_account['clash_tag'] == player.tag:
                            await con.execute(sql_update_discord_user_is_active(), True, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                            msg = account_panel(db_discord_member, db_clash_accounts, 'Clash account set')
                            self.log.info(msg)
                            await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                              ctx.author.id, msg)
                            await self._set_defaults(ctx, member, player.town_hall, player.name)
                            return

                    await self._multi_account_logic(ctx, coc_record, member, player, args)

                else:
                    self.log.error(f'Invalid condition met with args {arg_string}')

        await self._set_defaults(ctx, member, player.town_hall, player.name)

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
                    await self.bot.embed_print(ctx, msg, color=self.bot.SUCCESS)
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


