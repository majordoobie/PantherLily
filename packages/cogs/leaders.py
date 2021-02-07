from asyncio import TimeoutError
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
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Leaders')

    async def _get_updates(self, member_id: int) -> tuple:
        """Method gets the most up to date user information - this code is repeated a lot in this class"""
        async with self.bot.pool.acquire() as con:
            db_discord_member = await con.fetchrow(sql_select_discord_user_id(), member_id)
            db_clash_accounts = await con.fetch(sql_select_clash_account_discord_id(), member_id)
        return db_discord_member, db_clash_accounts

    async def _multi_account_logic(self, ctx, coc_record, member, player, args):
        """Repeated code in add_user"""
        async with self.bot.pool.acquire() as con:
            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
            if not args['coc_alternate']:
                msg = alternate_account(db_discord_member, db_clash_accounts, args)
                self.log.error(msg)
                await self.bot.send(ctx, msg, title='Multiple clash accounts', color=self.bot.WARNING)
                # if the user added the flag then add the new clash account and set it to primary
            else:
                await con.execute(sql_update_discord_user_is_active(), True, member.id)
                await con.execute(sql_update_clash_account_coc_alt_cascade(), False, member.id)
                await con.execute(sql_insert_clash_account(), *coc_record)
                db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                msg = account_panel(db_discord_member, db_clash_accounts, "Alternate clash account set")
                self.log.error(msg)
                await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                  ctx.author.id, msg)

                await self._set_defaults(ctx, member, player.town_hall, player.name)

    async def _set_defaults(self, ctx, member, clash_level: int, in_game_name: str):
        """Set default roles and name change"""
        default_roles = get_default_roles(ctx.guild, self.bot.settings, clash_level)

        if default_roles is None:
            msg = f'Unable to retrieve `th{clash_level}s` role or `CoC Members` role. please make sure it ' \
                  f'exits for me to automatically assign it to users.'
            await self.bot.send(ctx, msg, title='Role not found', color=self.bot.ERROR)
        else:
            try:
                await member.add_roles(*default_roles)
                for role in default_roles:
                    self.bot.log_role_change(member, role, log=self.log)
            except Exception as error:
                self.bot.log.error(error, exc_info=True)
                exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
                await self.bot.send(ctx, exc, title='User role change error', color=self.bot.ERROR)

        try:
            if member.display_name != in_game_name:
                old_name = member.display_name
                await member.edit(nick=in_game_name, reason='Panther Bot')
                self.log.error(f'Changed `{old_name}` name to `{in_game_name}`')
        except Exception as error:
            self.bot.log.critical(error, exc_info=True)
            exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
            await self.bot.send(ctx, exc, title='Unable to change users nickname', color=self.bot.ERROR)

    async def _remove_defaults(self, member):
        keep_roles = []
        remove_roles = []
        for role in member.roles[1:]:  # skip the first role @everyone
            if role.name not in self.bot.settings.default_roles:
                keep_roles.append(role)
            else:
                remove_roles.append(role)

        await member.edit(roles=keep_roles)
        for role in remove_roles:
            self.bot.log_role_change(member, role, log=self.log, removed=True)

    async def _remove_user(self, ctx, member_id, clash_tag, kick_message=None):
        async with self.bot.pool.acquire() as con:
            await con.execute(sql_update_discord_user_is_active(), False, member_id)
            db_discord_member, db_clash_accounts = await self._get_updates(member_id)
            if kick_message:
                msg = account_panel(db_discord_member, db_clash_accounts, f'Kick Message:\n{kick_message}')
            else:
                msg = account_panel(db_discord_member, db_clash_accounts, 'User set to inactive')
            self.log.error(msg)
            await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
            await con.execute(sql_insert_user_note(), member_id, clash_tag, datetime.now(), ctx.author.id, msg)

    @commands.check(is_leader)
    @commands.command(
        aliases=['remove_user'],
        brief='',
        description='Remover user from Panther Lily',
        usage='[-m str]',
        help='Removing user from Panther Lily does not delete them, it only sets their trackers off. Their '
             'data, especially their admin notes, will remain for later access.\n\n'
             'You are able to use this with or without the -m switch.\n\n'
             '-m || --message'
    )
    async def remove(self, ctx, *, arg_string=None):
        arg_dict = {
            'kick_message': {
                'flags': ['-m', '--message'],
            }
        }

        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="remove",
                                   args=args,
                                   arg_string=arg_string)

        if not args['positional']:
            await self.bot.send(ctx, 'You must provide the discord user as an argument', color=self.bot.WARNING)
            return

        member = await get_discord_member(ctx, args['positional'], self.bot.send)
        if member is None:
            return

        clash_tag = None
        async with self.bot.pool.acquire() as con:
            clash_accounts = await con.fetch(sql_select_clash_account_discord_id(), member.id)

        for clash_account in clash_accounts:
            if clash_account['is_primary_account']:
                clash_tag = clash_account['clash_tag']
        if not clash_tag:
            clash_tag = clash_accounts[0]['clash_tag']

        if args['kick_message']:
            await self._remove_user(ctx, member.id, clash_tag, kick_message=args['kick_message'])
            await self._remove_defaults(member)
        else:
            def check(reaction, user):
                if user == ctx.author:
                    if reaction.emoji.name in ['check', 'delete']:
                        return True

            msg = 'You are about to remove user without a reason message. Click the check box to continue otherwise ' \
                  f'use the following:\n\n `p.remove {arg_string}`\n`-m "User note message"`'
            raw_embeds = await self.bot.send(ctx, msg, _return=True)
            for embed in raw_embeds:
                embed_object = await ctx.send(embed=embed)
            await embed_object.add_reaction(self.bot.settings.emojis['check'])
            await embed_object.add_reaction(self.bot.settings.emojis['delete'])

            reaction, user = None, None
            try:
                reaction, user = await self.bot.wait_for('reaction_add', timeout=30, check=check)
            except TimeoutError:
                pass
            finally:
                await embed_object.clear_reactions()

            if reaction.emoji.name == 'delete':
                return

            else:
                await self._remove_user(ctx, member.id, clash_tag)
                await self._remove_defaults(member)

    @commands.check(is_leader)
    @commands.command(
        aliases=['add_user'],
        brief='',
        description='Register user to Panther Lily',
        usage='[-c(str)] [-d(str)] [--set-alternate]',
        help='Register a new user, a returning user, or set an alternate Clash of Clans account.\n\n'
             '-c || --clash-tag\n-d || --discord-id\n--set-alternate'
    )
    async def add(self, ctx, *, arg_string=None):
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash-tag', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord-id', '-d'],
                'required': True,
                'type': 'int'
            },
            'coc_alternate': {
                'flags': ['--set-alternate'],
                'switch': True,
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="add",
                                   args=args,
                                   arg_string=arg_string)

        if not args:
            return

        # Get user objects
        player = await get_coc_player(ctx, args['coc_tag'], self.bot.coc_client, self.bot.send)
        member = await get_discord_member(ctx, args['discord_id'], self.bot.send)
        if not player or not member:
            return

        member: Member
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
                self.log.error(f'Adding new user {member.name} with clash of {player.tag}')
                await con.execute(sql_insert_discord_user(), *discord_record)
                await con.execute(sql_insert_clash_account(), *coc_record)
                db_discord_member, db_clash_accounts = await self._get_updates(member.id)

                msg = account_panel(db_discord_member, db_clash_accounts, "New user added")
                await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(), ctx.author.id, msg)
                self.log.error(msg)
                await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                await self._set_defaults(ctx, member, player.town_hall, player.name)

            # If user HAS a discord account BUT their active state is set to false
            elif db_discord_member['is_active'] == False:
                self.log.error(
                    f'Discord member `{member.name}:{member.id}` already exits, but `is_active` attribute is '
                    f'set to `false`')

                # If they have 0 clash accounts then their main account was probably removed so just add one and move on
                if len(db_clash_accounts) == 0:
                    await con.execute(sql_update_discord_user_is_active(), True, member.id)
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                    msg = account_panel(db_discord_member, db_clash_accounts, "User enabled")
                    self.log.error(msg)
                    await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                    await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(), ctx.author.id, msg)
                    await self._set_defaults(ctx, member, player.town_hall, player.name)

                # If they have one account - then we need to see if the clash tag they are adding is the same
                elif len(db_clash_accounts) == 1:
                    # If the clash tag arg is the same that is in the database then we are just enabling their account
                    if db_clash_accounts[0]['clash_tag'] == player.tag:
                        await con.execute(sql_update_discord_user_is_active(), True, member.id)
                        await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                        db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                        msg = account_panel(db_discord_member, db_clash_accounts, "User enabled")
                        self.log.error(msg)
                        await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                        await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                          ctx.author.id, msg)
                        await self._set_defaults(ctx, member, player.town_hall, player.name)

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
                            self.log.error(msg)
                            await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
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
                    self.log.error(msg)
                    await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                    await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                      ctx.author.id, msg)
                    await self._set_defaults(ctx, member, player.town_hall, player.name)

                elif len(db_clash_accounts) == 1:
                    if db_clash_accounts[0]['clash_tag'] == player.tag:
                        if db_clash_accounts[0]['is_primary_account']:
                            msg = account_panel(db_discord_member, db_clash_accounts, 'No action taken')
                            self.log.error(msg)
                            await self.bot.send(ctx, msg)

                        else:
                            await con.execute(sql_update_clash_account_coc_alt_primary(), True, member.id, player.tag)
                            db_discord_member, db_clash_accounts = await self._get_updates(member.id)
                            msg = account_panel(db_discord_member, db_clash_accounts, 'Clash account set')
                            self.log.error(msg)
                            await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                              ctx.author.id, msg)
                            await self._set_defaults(ctx, member, player.town_hall, player.name)
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
                            self.log.error(msg)
                            await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                            await con.execute(sql_insert_user_note(), member.id, player.tag, datetime.now(),
                                              ctx.author.id, msg)
                            await self._set_defaults(ctx, member, player.town_hall, player.name)
                            return

                    await self._multi_account_logic(ctx, coc_record, member, player, args)

                else:
                    self.log.critical(f'Invalid condition met with args {arg_string}')

    @commands.check(is_leader)
    @commands.command(
        aliases=['delete-coc-link', 'delete_coc_link'],
        brief='',
        description='Remove a Clash of Clans account from a Users account',
        usage='[-c] [-d]',
        help='Delete the link between a Clash of Clans account and a Panther Lily account.\n\n'
             '-c || --clash-tag\n-d || --discord-id'
    )
    async def del_coc(self, ctx, *, arg_string=None):
        arg_dict = {
            'coc_tag': {
                'flags': ['--clash-tag', '-c'],
                'required': True
            },
            'discord_id': {
                'flags': ['--discord-id', '-d'],
                'required': True,
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.log.warning(f'`{ctx.author.display_name}` ran `del_coc` with {args}')
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="del_coc",
                                   args=args,
                                   arg_string=arg_string)

        if not args:
            return

        player = await get_coc_player(ctx, args['coc_tag'], self.bot.coc_client, self.bot.send)
        member = await get_discord_member(ctx, args['discord_id'], self.bot.send)
        if not player or not member:
            return

        async with self.bot.pool.acquire() as con:
            discord_member = await con.fetchrow(sql_select_discord_user_id(), member.id)
            clash_accounts = await con.fetch(sql_select_clash_account_discord_id(), member.id)
            for clash_account in clash_accounts:
                if clash_account['clash_tag'] == player.tag:
                    await con.execute(sql_delete_clash_account_record(), player.tag, member.id)
                    clash_accounts = await con.fetch(sql_select_clash_account_discord_id(), member.id)
                    msg = f'Removed `{player.tag}` from `{member.name}:{member.id}`\n{account_panel(discord_member, clash_accounts)}'
                    self.log.error(msg)
                    await self.bot.send(ctx, msg, color=self.bot.SUCCESS)
                    return
            await self.bot.send(ctx,
                                f"Nothing to delete, check commands\n{account_panel(discord_member, clash_accounts)}")

    @commands.check(is_leader)
    @commands.command(
        aliases=['v', 'view_account'],
        brief='',
        description='View players account information',
        usage='(user_name)',
        help='Display the users information such as all the Clash of Clans account associated with them.'
             'The command takes a users name or clash tag as a argument.'
    )
    async def view(self, ctx, *, arg_string=None):
        arg_dict = {}
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="view",
                                   args=args,
                                   arg_string=arg_string)

        if args['positional']:
            member = await get_discord_member(ctx, args['positional'], self.bot.send)
            if not member:
                return
        else:
            member = ctx.author

        db_discord_member, db_clash_accounts = await self._get_updates(member.id)
        msg = account_panel(db_discord_member, db_clash_accounts)
        await self.bot.send(ctx, msg, color=self.bot.SUCCESS)

    @commands.check(is_leader)
    @commands.command(
        aliases=['re'],
        brief='',
        description='View donation report',
        usage='[-w (int)]',
        help='Show the donation report of all users in the clan. You are also able to display previous weeks'
             'by providing the number of weeks to display.\n\n'
             '-w || --weeks'
    )
    async def report(self, ctx, *, arg_string=None):
        arg_dict = {
            'weeks': {
                'flags': ['-w', '--weeks'],
                'type': 'int',
                'default': 1
            }
        }
        args = await parse_args(ctx, self.bot.settings, arg_dict, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="report",
                                   args=args,
                                   arg_string=arg_string)

        true = self.bot.settings.emojis['true']
        false = self.bot.settings.emojis['false']
        warning = '<:warning:807778609825447968>'

        # Get the amount of weeks to pull back
        dates = []
        current_week = get_utc_monday()
        for i in range(0, args['weeks']):
            dates.append(get_utc_monday() - timedelta(days=(i * 7)))

        # Get report blocks based on dates
        async with self.bot.pool.acquire() as con:
            for date in dates:
                players = await con.fetch(sql_select_classic_view().format(date))
                players.sort(key=lambda x: x['donation_gains'], reverse=True)
                data_block = f"`\u00A0\u00A0\u00A0 {'Player':<14}⠀` `⠀{'Donation'}⠀`\n"
                for player in players:
                    donation = player['donation_gains']
                    emoji = true if donation > 300 else false
                    if date == current_week:
                        if not player["guild_join_date"] < current_week:
                            emoji = warning
                    data_block += f"{emoji}\u00A0`⠀" \
                                  f"{player['clash_name']:<17.17}⠀` `⠀{donation:⠀>5}⠀`\n"

                embeds = await self.bot.send(ctx, data_block, _return=True, footnote=False)
                date = f"Week of: {date.strftime('%Y-%m-%d')} (GMT)"
                if isinstance(embeds, list):
                    embeds[-1].set_footer(text=date)
                    for embed in embeds:
                        await ctx.send(embed=embed)
                else:
                    embeds.set_footer(text=date)
                    await ctx.send(embed=embeds)


def account_panel(discord_member: dict, coc_accounts: list, title: str = '') -> str:
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
