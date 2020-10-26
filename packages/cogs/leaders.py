from datetime import datetime

from discord.ext import commands
import logging

from bot import BotClient

from packages.cogs.utils.bot_sql import *
from packages.cogs.utils.utils import *


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger('root.Leaders')

    @commands.check(is_leader)
    @commands.command(aliases=['user_add'])
    async def add_user(self, ctx, *, arg_string=None):
        # Set up arguments 9P9PRYQJ 265368254761926667
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
            self.log.debug(f'Attempting to add user `{member.name}:{member.id}`')

            discord_member = await con.fetchrow(sql_select_discord_user_id(), member.id)
            clash_members = await con.fetch(sql_select_clash_account_discordid(), member.id)

            # If clash and discord do not exist
            if discord_member is None and not clash_members:
                self.log.info(f'Adding new user {member.name} with clash of {player.tag}')
                await con.execute(sql_insert_discord_user(), *discord_record)
                await con.execute(sql_insert_clash_account(), *coc_record)

            # If member activity is set to false
            elif not discord_member['is_active']:
                self.log.info(f'Discord member `{member.name}:{member.id}` already exits, but `is_active` attribute is '
                              f'set to `false`')

                if len(clash_members) == 0:
                    await con.execute(sql_update_discord_user_is_active(), True, member.id)
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    msg = f'Set discord user {member.name}:{member.id} `is_active` attribute to `True` with clash account ' \
                          f'`{player.tag}`'
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg)

            elif discord_member['is_active']:
                if len(clash_members) == 0:
                    await con.execute(sql_insert_clash_account(), *coc_record)
                    msg = f'Discord user `{member.name}:{member.id}` already exits and `is_active` attribute is set ' \
                          f'to `True`. Adding clash account `{player.tag}`'
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg)
                    return

                elif len(clash_members) == 1:
                    if clash_members[0]['clash_tag'] == player.tag:
                        msg = f'Discord member `{member.name}:{member.id}` is already active with the clash account ' \
                              f'of `{player.tag}`; skipping...'
                        self.log.info(msg)
                        await self.bot.embed_print(ctx, msg)
                        return

                    else:
                        if not args['coc_alternate']:
                            msg = f'Discord member `{member.name}:{member.id}` already has a clash account of ' \
                                  f'`{player.tag}` if you would like to add another clash account please use the following ' \
                                  f'command:\n\n `{arg_string} --set-alternate`'
                            self.log.warning(msg)
                            await self.bot.embed_print(ctx, msg, color='warning')
                            return

                        else:
                            await con.execute(sql_update_clash_account_coc_alt(), False, member.id)
                            await con.execute(sql_insert_clash_account(), *coc_record)
                            clash_accounts = await con.fetch(sql_select_clash_account_discordid(), member.id)
                            acc_panel = account_panel(discord_member, clash_accounts)
                            msg = f'Added alternate account to `{member.name}`\n' \
                                  f'\nSet `{player.tag} -> Primary`\n\n{acc_panel}'
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
                    msg = f'Removed `{player.tag} from `{member.name}:{member.id}`'
                    self.log.info(msg)
                    await self.bot.embed_print(ctx, msg)
                    await self.bot.embed_print(ctx, account_panel(discord_member, clash_accounts))
                    return
            acc_panel = account_panel(discord_member, clash_accounts)
            await self.bot.embed_print(ctx, acc_panel)

def account_panel(discord_member, coc_accounts: list) -> str:
    coc_panel = f'`{"Clash Tag":<15}` `{"Primary":<15}`\n'
    for coc_account in coc_accounts:
        coc_bool = "True" if coc_account['is_primary_account'] else "False"
        coc_panel += f'`{coc_account["clash_tag"]:<15}` `{coc_bool:<15}`\n'
        #coc_panel += f'`{"Clash Account:":<15}` `{coc_account["clash_tag"]}` `{"Is Primary:":<15}` `{coc_account["is_primary_account"]}`\n'

    if coc_panel == '':
        coc_panel = "No CoC Accounts Bound"

    return f'**Player Account**\n\n' \
           f'`{"Discord Name:":<14}` `{discord_member["discord_nickname"]}`\n' \
           f'`{"Is Active:":<14}` `{discord_member["is_active"]}`\n' \
           f'\n**Clash Accounts**:\n' \
           f'{coc_panel}'



def setup(bot):
    bot.add_cog(Leaders(bot))


