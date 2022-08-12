import disnake
import asyncpg
import json
import logging
from typing import List, Union, Optional, Tuple

from disnake.ext import commands
from disnake import RawReactionActionEvent, Message

from bot import BotClient
from packages.utils.utils import EmbedColor, parse_args

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
    POOL = None

    def __init__(self, bot: BotClient):
        self.bot = bot
        self.pool = self.bot.pool
        Happy.POOL = self.pool
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Happy')
        self.emojis = {emoji: self.bot.settings.emojis[emoji] for emoji in
                       EMOJI_REACTIONS}

    @staticmethod
    async def panel_names(inter: disnake.ApplicationCommandInteraction,
                          user_input: str) -> List[str]:

        if not Happy.POOL:
            return [""]

        async with Happy.POOL.acquire() as conn:
            sql = "SELECT panel_name FROM happy"
            rows = await conn.fetch(sql)

        return [panel["panel_name"] for panel in rows if user_input.title()
                in panel["panel_name"]]

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
            sql = "SELECT * FROM happy WHERE message_id=$1"
            record = await con.fetchrow(sql, payload.message_id)

        # If message ID is not part of the Happy table, then ignore
        if not record:
            return

        # Confirm that the emoji object is one that we support
        if str(payload.emoji) not in self.emojis.values():
            return

        # Get the message object to edit it
        message = await self._get_message(record["message_id"],
                                          payload.channel_id, payload.guild_id)
        if not message:
            return

        # Reset the panel reaction
        await message.remove_reaction(payload.emoji, payload.member)

        # The panel should be active, but if it is not then clear the reactions and update the db
        # What to do when stop is called
        if str(payload.emoji) == self.emojis["stop"] or not record["active"]:
            await self._refresh_panel(record, message)
            await message.clear_reactions()
            sql = "UPDATE happy SET active=False WHERE message_id=$1"
            async with self.bot.pool.acquire() as con:
                await con.execute(sql, payload.message_id)

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
            _dict = record['data']
            sql = "UPDATE happy SET data=$1 WHERE panel_name=$2"
            await con.execute(sql, _dict, record['panel_name'])

        # Automatically remove reactions when panel is full
        done = True
        for index, value in enumerate(record["data"].values()):
            if index >= record["panel_rows"]:
                continue
            if value is None:
                done = False
        if record["data"]["topoff2"] is None:
            done = False
        if record["data"]["super_troop"] is None:
            done = False

        # If done, remove reactions and set panel to false
        if done:
            record = dict(record)
            record["active"] = False
            await self._refresh_panel(record, message)
            await message.clear_reactions()
            sql = "UPDATE happy SET active=$1 WHERE panel_name=$2"
            async with self.bot.pool.acquire() as con:
                await con.execute(sql, False, record['panel_name'])

    async def _refresh_panel(self, record: Union[asyncpg.Record, dict],
                             message: Message, reset_emojis=False):
        panel, emoji_stack = self._panel_factory(record)
        embeds = await self.bot.send(ctx=None, description=panel,
                                     footnote=False, _return=True)
        for embed in embeds:
            await message.edit(embed=embed)

        if reset_emojis:
            await message.clear_reactions()
            for reaction in emoji_stack:
                await message.add_reaction(reaction)

    async def _get_message(self, message_id: int, channel_id: int,
                           guild_id: int) -> Optional[Message]:
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

    async def _panel_exists(self,
                            inter: disnake.ApplicationCommandInteraction,
                            panel_name: Union[str, None]
                            ) -> Optional[asyncpg.Record]:
        """
        Check to see if the given panel_name exits in the database. If it does
        then return the record for it.

        :param inter:
        :param panel_name: Name of the panel to look up
        :return:
        """
        if not panel_name:
            await self.bot.inter_send(
                inter,
                panel="Please provide a panel name to delete. You can use "
                      "the `Panther.Happy list` command to view all the "
                      "panels available to you.",
                color=EmbedColor.WARNING)
            return None

        panel_name = panel_name.title()

        async with self.bot.pool.acquire() as conn:
            sql = "SELECT * FROM happy WHERE panel_name=$1"
            row = await conn.fetchrow(sql, panel_name)

        if not row:
            await self.bot.inter_send(
                inter,
                panel=f'Could not find a panel with the name '
                      f'of `{panel_name}`',
                color=EmbedColor.WARNING)
            return None

        else:
            return row

    @commands.slash_command(
        name="happy",
        dm_permission=False,
        auto_sync=True
    )
    async def happy(self, ctx, *, arg_string=None):
        pass

    @happy.sub_command(
        name='delete'
    )
    async def delete_panel(
            self,
            inter: disnake.ApplicationCommandInteraction,
            panel_name: str = commands.Param(
                autocomplete=panel_names)) -> None:
        """
        Delete a panel from the /happy list

        Parameters
        ----------
        inter:
        panel_name: Name of panel to remove, use /happy list to find name
        """
        if panel_name not in await self.panel_names(inter, panel_name):
            await self.bot.inter_send(
                inter,
                panel=f"Panel **{panel_name}** does not exist. Please use "
                      f"/happy list",
                color=EmbedColor.WARNING)
            return

        async with self.bot.pool.acquire() as conn:
            sql = "DELETE FROM happy WHERE panel_name=$1"
            await conn.execute(sql, panel_name)

        await self.bot.inter_send(
            inter,
            panel=f'Deleted panel `{panel_name}`!',
            color=EmbedColor.SUCCESS)

    @happy.sub_command(
        name='create'
    )
    async def create_panel(self,
                           inter: disnake.ApplicationCommandInteraction,
                           panel_name: str,
                           row_count: int = commands.Range[1, 10]):
        # Split the positional arguments and make sure that it's str and
        # str(int)
        try:
            panel_name, panel_rows = args["positional"].split(' ')
            panel_name = panel_name.title()
            if not panel_rows.isdigit():
                msg = f'The second argument must be an integer between 1 and 10. You provided `{panel_rows}`'
                await self.bot.send(inter, msg, color=EmbedColor.ERROR)
                return
            else:
                panel_rows = int(panel_rows)
                if not 1 <= panel_rows <= 10:
                    msg = f'The number of rows you provided does not fall within 1 and 10.'
                    await self.bot.send(inter, msg, EmbedColor.ERROR)
                    return
        except ValueError:
            msg = f'Too many arguments provided. Args: `{args["positional"]}`\nCommand only takes 2. A name ' \
                  f'followed by the number of rows to populate.'
            await self.bot.send(inter, msg, EmbedColor.ERROR)
            self.log.error(
                f'{inter.author.display_name} provided too many arguments to command: {args}')
            return

        async with self.bot.pool.acquire() as conn:
            sql = "SELECT panel_name FROM happy WHERE panel_name=$1"
            sql2 = f"""INSERT INTO happy (panel_name, panel_rows, active, message_id, channel_id, guild_id, data) VALUES 
            ($1, $2, $3, $4, $5, $6, $7)"""

            if await conn.fetchrow(sql, panel_name):
                await self.bot.send(inter,
                                    f'Panel `{panel_name}` already exists.',
                                    EmbedColor.WARNING)
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
                await self.bot.send(inter, f'Panel `{panel_name}` created!',
                                    EmbedColor.SUCCESS, footnote=False)

    @happy.sub_command(
        name='view'
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
            await self.bot.send(ctx, msg, EmbedColor.WARNING)
            return

        instance = dict(instance)
        instance["active"] = True
        panel, emoji_stack = self._panel_factory(instance)
        embeds = await self.bot.send(ctx, panel, footnote=False, _return=True)
        for embed in embeds:
            panel = await ctx.send(embed=embed)
        for emoji in emoji_stack:
            await panel.add_reaction(emoji)

        async with self.bot.pool.acquire() as conn:
            sql = "UPDATE happy SET message_id=$1, active=$2, channel_id=$3, guild_id=$4 WHERE panel_name=$5"
            await conn.execute(sql, panel.id, True, panel.channel.id,
                               panel.guild.id, instance['panel_name'])

    @happy.sub_command(
        name='clear'
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
            sql = "UPDATE happy SET data=$1 WHERE panel_name=$2"
            sql2 = "SELECT * FROM happy WHERE panel_name=$1"
            await con.execute(sql, self.default_dataset,
                              instance['panel_name'])
            instance = await con.fetchrow(sql2, instance['panel_name'])

        if instance["active"]:
            message = await self._get_message(instance["message_id"],
                                              instance["channel_id"],
                                              instance["guild_id"])
            if not message:
                return
            await self._refresh_panel(instance, message)
        else:
            await self.bot.send(ctx, 'Cleared panel', EmbedColor.SUCCESS,
                                footnote=False)

    @happy.sub_command(
        name='stop'
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
            sql = "UPDATE happy SET active=$1 WHERE panel_name=$2"
            await con.execute(sql, False, instance['panel_name'])

        message = await self._get_message(instance["message_id"],
                                          instance["channel_id"],
                                          instance["guild_id"])
        if not message:
            return
        instance = dict(instance)
        instance["active"] = False
        await self._refresh_panel(instance, message)
        await message.clear_reactions()
        await self.bot.send(ctx, 'Stopped panel from running.',
                            EmbedColor.SUCCESS, footnote=False)

    @happy.sub_command(
        name='list'
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

        panel = f'{"NAME":<15} {"ROWS":<5} {"ACTIVE"}\n'
        for row in rows:
            active = "T" if row["active"] else "F"
            panel += f'{row["panel_name"]:<18} {row["panel_rows"]:<2} {active:<1}\n'
        await self.bot.send(ctx, panel, code_block=True)

    @happy.sub_command(
        name='edit'
    )
    async def edit_panel(self, ctx, *, arg_string=None):
        args = await parse_args(ctx, self.bot.settings, {}, arg_string)
        self.bot.log_user_commands(self.log,
                                   user=ctx.author.display_name,
                                   command="happy edit_panel",
                                   args=args,
                                   arg_string=arg_string)

        string_objects = args["positional"].split(' ')

        instance = await self._panel_exists(ctx, string_objects[0])
        if not instance:
            return

        if len(string_objects) not in [2, 3]:
            await self.bot.send(ctx,
                                'Invalid arguments used. Please see the help menu.')
            return
        elif len(string_objects) == 2:
            try:
                operator, integer = string_objects[1][0], string_objects[1][1:]
            except:
                await self.bot.send(ctx,
                                    'Invalid arguments used. Please see the help menu.',
                                    EmbedColor.ERROR)
                return
        else:
            operator, integer = string_objects[1], string_objects[2]

        if operator not in ['+', '-']:
            await self.bot.send(ctx, 'Invalid operators used',
                                EmbedColor.ERROR)
            return
        if not integer.isdigit():
            await self.bot.send(ctx, 'Invalid integer provided',
                                EmbedColor.ERROR)
            return
        elif int(integer) not in range(0, 11):
            await self.bot.send(ctx, 'Invalid integer range provided',
                                EmbedColor.ERROR)
            return

        if operator == '+':
            new_rows = instance["panel_rows"] + int(integer)
        else:
            new_rows = instance["panel_rows"] - int(integer)
        if new_rows not in range(0, 11):
            await self.bot.send(ctx, 'New row count exceeds range of 0 to 10',
                                EmbedColor.ERROR)
            return

        async with self.bot.pool.acquire() as con:
            sql = "UPDATE happy SET panel_rows=$1 WHERE panel_name=$2"
            await con.execute(sql, new_rows, instance['panel_name'])

        instance = await self._panel_exists(ctx, instance["panel_name"])
        message = await self._get_message(instance["message_id"],
                                          instance["channel_id"],
                                          instance["guild_id"])
        await self.bot.send(ctx, 'Panel edited', EmbedColor.SUCCESS,
                            footnote=False)
        if instance["active"]:
            await self._refresh_panel(instance, message, reset_emojis=True)

    def _panel_factory(self, instance) -> Tuple[str, list]:
        ranges = ['1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25',
                  '26 - 30', '31 - 35', '36 - 40',
                  '41 - 45', '46 - 50']

        data = instance["data"]
        emoji_stack = []

        status = 'Active' if instance["active"] else 'Inactive'
        panel = f'**Panel Name:**   `{instance["panel_name"]}`\n' \
                f'**Panel Status:** `{status}`\n\n'

        for i in range(0, instance["panel_rows"]):
            emoji = self.emojis[f'h{i + 1}']
            emoji_stack.append(emoji)
            key = f'h{i + 1}'
            panel += f'{emoji} `[{ranges[i]:>7}]: {data[key] if data[key] else "":<20}`\n'

        panel += f'{self.emojis["topoff2"]} `[{"Topoff":>7}]: {data["topoff2"] if data["topoff2"] else "":<20}`\n'
        panel += f'{self.emojis["super_troop"]} `[{"Super":>7}]: {data["super_troop"] if data["super_troop"] else "":<20}`\n'
        emoji_stack.append(self.emojis["topoff2"])
        emoji_stack.append(self.emojis["super_troop"])
        emoji_stack.append(self.emojis["stop"])

        return panel, emoji_stack


def setup(bot):
    bot.add_cog(Happy(bot))
