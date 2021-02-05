from asyncpg import pool, Record
import json
import logging
from typing import Union, Optional, Tuple

from discord.ext import commands
from discord import RawReactionActionEvent, Message

from bot import BotClient
from packages.cogs.utils.utils import parse_args

EMOJI_REACTIONS = (
    'h1',
    'h2',
    'h3',
    'h4',
    'h5',
    'h6',
    'h7',
    'h8',
    'h9',
    'h10',
    'stop',
    'topoff2',
    'super_troop',
)


class Happy(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.poo: pool
        self.pool = self.bot.pool
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Happy')
        self.emojis = {emoji: self.bot.settings.emojis[emoji] for emoji in EMOJI_REACTIONS}

    @property
    def default_dataset(self) -> dict:
        """Return the default data parameter"""
        return {
                'h1': None,
                'h2': None,
                'h3': None,
                'h4': None,
                'h5': None,
                'h6': None,
                'h7': None,
                'h8': None,
                'h9': None,
                'h10': None,
                "topoff2": None,
                "super_troop": None
            }

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: RawReactionActionEvent):
        # Ignore bot chatter
        if payload.member.bot:
            return

        # Check to see if it is a panel that exits in the database
        async with self.bot.pool.acquire() as con:
            sql = f"""SELECT * FROM happy WHERE message_id={payload.message_id}"""
            record = await con.fetchrow(sql)

        # If message ID is not part of the Happy table, then ignore
        if not record:
            return

        # Confirm that the emoji object is one that we support
        if str(payload.emoji) not in self.emojis.values():
            return

        # Get the message object to edit it
        message = await self._get_message(record["message_id"], payload.channel_id, payload.guild_id)
        if not message:
            return

        # Reset the panel reaction
        await message.remove_reaction(payload.emoji, payload.member)

        # The panel should be active, but if it is not then clear the reactions and update the db
        # What to do when stop is called
        if str(payload.emoji) == self.emojis["stop"] or not record["active"]:
            await message.clear_reactions()
            sql = f"""UPDATE happy SET active=False WHERE message_id={payload.message_id}"""
            async with self.bot.pool.acquire() as con:
                await con.execute(sql)

            return

        # Check to see if user is adding or removing their choice
        current_user = record["data"][payload.emoji.name]
        if current_user == payload.member.display_name:
            record["data"][payload.emoji.name] = None
        else:
            record["data"][payload.emoji.name] = payload.member.display_name

        await self._refresh_panel(record, message)

        # Update the database
        async with self.bot.pool.acquire() as con:
            _dict = json.dumps(record["data"])
            sql = f"""UPDATE happy SET data='{_dict}' WHERE panel_name='{record["panel_name"]}' """
            await con.execute(sql)

    async def _refresh_panel(self, record: Record, message: Message):
        panel, emoji_stack = self._panel_factory(record)
        embeds = await self.bot.send(ctx=None, description=panel, footnote=False, _return=True)
        for embed in embeds:
            await message.edit(embed=embed)

    async def _get_message(self, message_id: int, channel_id: int, guild_id: int) -> Optional[Message]:
        """Get a message object"""
        guild, channel, message = None, None, None
        try:
            guild = self.bot.get_guild(guild_id)
            channel = guild.get_channel(channel_id)
            message: Message
            message = await channel.fetch_message(message_id)
        except Exception:
            msg = f'Could not find the message object\n' \
                  f'Guild ID: {guild_id}\n' \
                  f'Guild obj: {guild}\n' \
                  f'Channel ID: {channel_id}\n' \
                  f'Channel obj: {channel}\n' \
                  f'Message ID: {message_id}\n' \
                  f'Message obj: {message}\n\n'

            self.log.error(msg, exc_info=True)

            return None
        return message

    async def _panel_exists(self, ctx: commands.Context, panel_name: Union[str, None]) -> Optional[Record]:
        """
        Check to see if the given panel_name exits in the database. If it does then return the record for it.
        Parameters
        ----------
        ctx: commands.Context
            Context of the command ran
        panel_name: str
            String name of the panel name at question

        Returns
        -------
        Either the record if there is a match or a None

        """
        if not panel_name:
            await self.bot.send(ctx, "Please provide a panel name to delete. You can use the `Panther.Happy "
                                      "list` command to view all the panels available to you.",
                                      color=self.bot.WARNING)
            return None

        panel_name = panel_name.title()

        async with self.bot.pool.acquire() as conn:
            sql = f"""SELECT * FROM happy WHERE panel_name='{panel_name}' """
            row = await conn.fetchrow(sql)

        if not row:
            await self.bot.send(ctx, f'Could not find a panel with the name of `{panel_name}`',
                                       color=self.bot.WARNING)
            return None

        else:
            return row

    @commands.group(
        aliases=['h'],
        invoke_without_command=True,
        brief='',
        description='Create and View interactive panels to volunteer for zones to donate to for war preparations. '
                    'Users are able to click on the emojis to add their name to the panel board.',
        usage='',
        help=''
    )
    async def happy(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy",
                                   args=args,
                                   arg_string=arg_string)

        msg = f'Welcome to the Happy module! To see what I can do, run `panther.help Happy`'
        await self.bot.send(ctx, msg)

    @happy.command(
        name='delete',
        aliases=['d'],
        brief='',
        help='Delete the panel specified',
        usage='(panel_name)'
    )
    async def delete_panel(self, ctx, *, arg_string=None):
        """Create the panel to be viewed"""
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy delete",
                                   args=args,
                                   arg_string=arg_string)

        # Check if panel_name exists, if it does return the record
        panel_name = await self._panel_exists(ctx, args["positional"])
        if not panel_name:
            return

        async with self.bot.pool.acquire() as conn:
            sql = f"""DELETE FROM happy WHERE panel_name='{panel_name["panel_name"]}' """
            await conn.execute(sql)
        await self.bot.send(ctx, f'Deleted panel `{panel_name["panel_name"]}`!', color=self.bot.SUCCESS)

    @happy.command(
        name='create',
        aliases=['cr'],
        brief='',
        help='Crete a panel by providing the name of a panel and the number of rows you would like to '
             'create.\n\n'
             'Example:\n'
             'p.h create sunday_war 10',
        usage='(panel_name) (rows)'
    )
    async def create_panel(self, ctx, *, arg_string=None):
        """Create the panel to be viewed"""
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy create",
                                   args=args,
                                   arg_string=arg_string)
        # Split the positional arguments and make sure that it's str and str(int)
        try:
            panel_name, panel_rows = args["positional"].split(' ')
            panel_name = panel_name.title()
            if not panel_rows.isdigit():
                msg = f'The second argument must be an integer between 1 and 10. You provided `{panel_rows}`'
                await self.bot.send(ctx, msg, color=self.bot.ERROR)
                return
            else:
                panel_rows = int(panel_rows)
                if not 1 <= panel_rows <=10:
                    msg = f'The number of rows you provided does not fall within 1 and 10.'
                    await self.bot.send(ctx, msg, color=self.bot.ERROR)
                    return
        except ValueError:
            msg = f'Too many arguments provided. Args: `{args["positional"]}`\nCommand only takes 2. A name ' \
                  f'followed by the number of rows to populate.'
            await self.bot.send(ctx, msg, color=self.bot.ERROR)
            self.log.error(f'{ctx.author.display_name} provided too many arguments to command: {args}')
            return

        async with self.bot.pool.acquire() as conn:
            sql = f"""SELECT panel_name FROM happy WHERE panel_name='{panel_name}' """
            sql2 = f"""INSERT INTO happy (panel_name, panel_rows, active, message_id, channel_id, guild_id, data) VALUES 
            ($1, $2, $3, $4, $5, $6, $7)"""

            if await conn.fetchrow(sql):
                await self.bot.send(ctx, f'Panel `{panel_name}` already exists.', color=self.bot.WARNING)
            else:

                await conn.execute(
                    sql2,
                    panel_name,
                    panel_rows,
                    False,
                    0,
                    0,
                    0,
                    self.default_dataset
                )
                await self.bot.send(ctx, f'Panel `{panel_name}` created!', color=self.bot.SUCCESS)

    @happy.command(
        name='view',
        aliases=['v'],
        brief='',
        help='Open a panel to start having users volunteer for zones to donate to',
        usage='(panel_name)'
    )
    async def view_panel(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy view_panel",
                                   args=args,
                                   arg_string=arg_string)

        instance = await self._panel_exists(ctx, args["positional"])
        if not instance:
            return

        if instance["active"]:
            msg = f'Panel `{instance["panel_name"]}` is already open. Please close it first.'
            await self.bot.send(ctx, msg, color=self.bot.WARNING)
            return

        panel, emoji_stack = self._panel_factory(instance)
        embeds = await self.bot.send(ctx, panel, footnote=False, _return=True)
        for embed in embeds:
            panel = await ctx.send(embed=embed)
        for emoji in emoji_stack:
            await panel.add_reaction(emoji)

        async with self.bot.pool.acquire() as conn:
            sql = f"""UPDATE happy SET message_id={panel.id}, 
                                       active=true,
                                       channel_id={panel.channel.id},
                                       guild_id={panel.guild.id}
                                       WHERE panel_name='{instance["panel_name"]}' """
            await conn.execute(sql)

    @happy.command(
        name='clear',
        aliases=['cl'],
        brief='',
        help='Clears all the reactions on a panel.',
        usage=('panel_name')
    )
    async def clear_panel(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy clear_panel",
                                   args=args,
                                   arg_string=arg_string)

        instance = await self._panel_exists(ctx, args["positional"])
        if not instance:
            return

        async with self.bot.pool.acquire() as con:
            _json = json.dumps(self.default_dataset)
            sql = f"""UPDATE happy SET data='{_json}' WHERE panel_name='{instance["panel_name"]}'"""
            sql2 = f"""SELECT * FROM happy WHERE panel_name='{instance["panel_name"]}' """
            await con.execute(sql)
            instance = await con.fetchrow(sql2)

        if instance["active"]:
            message = await self._get_message(instance["message_id"], instance["channel_id"], instance["guild_id"])
            if not message:
                return
            await self._refresh_panel(instance, message)
        else:
            await self.bot.send(ctx, 'Cleared panel')

    @happy.command(
        name='stop',
        aliases=['s'],
        brief='',
        help='Stop a panel from receiving reactions. This is useful if you get the error of a panel '
             'already being open and don\'t want to scoll up to close the panel with the reaction',
        usage='(panel_name)'
    )
    async def stop_panel(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy stop_panel",
                                   args=args,
                                   arg_string=arg_string)

        instance = await self._panel_exists(ctx, args["positional"])
        if not instance:
            return

        async with self.bot.pool.acquire() as con:
            sql = f"""UPDATE happy SET active=False WHERE panel_name='{instance["panel_name"]}'"""
            await con.execute(sql)

        message = await self._get_message(instance["message_id"], instance["channel_id"], instance["guild_id"])
        if not message:
            return
        await message.clear_reactions()
        await self.bot.send(ctx, 'Stopped panel from running.')




    @happy.command(
        name='list',
        aliases=['l'],
        brief='',
        help='List all panels that have been created',
        usage='(panel_name)'
    )
    async def list_panels(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy list_panels",
                                   args=args,
                                   arg_string=arg_string)
        async with self.bot.pool.acquire() as conn:
            sql = """SELECT * FROM happy"""
            rows = await conn.fetch(sql)

        panel = f'{"NAME":<10} {"#":<2} {"ACTIVE":<5}\n'
        for row in rows:
            active = "True" if row["active"] else "False"
            panel += f'{row["panel_name"]:<10} {row["panel_rows"]:<2} {active:<5}\n'
        await self.bot.send(ctx, panel, code_block=True)

    def _panel_factory(self, instance) -> Tuple[str, list]:
        ranges = ['1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 30', '31 - 35', '36 - 40',
                  '41 - 45', '46 - 50']

        data = instance["data"]
        emoji_stack = []

        panel = f'**Panel:** `{instance["panel_name"]}`\n'
        for i in range(0, instance["panel_rows"]):
            emoji = self.emojis[f'h{i + 1}']
            emoji_stack.append(emoji)
            key = f'h{i+1}'
            panel += f'{emoji} `[{ranges[i]:>7}]: {data[key] if data[key] else "":<20}`\n'

        panel += f'{self.emojis["topoff2"]} `[{"Top off":>7}]: {data["topoff2"] if data["topoff2"] else "":<20}`\n'
        panel += f'{self.emojis["super_troop"]} `[{"Super":>7}]: {data["super_troop"] if data["super_troop"] else "":<20}`\n'
        emoji_stack.append(self.emojis["topoff2"])
        emoji_stack.append(self.emojis["super_troop"])
        emoji_stack.append(self.emojis["stop"])

        return panel, emoji_stack






def setup(bot):
    bot.add_cog(Happy(bot))
