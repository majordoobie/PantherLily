import disnake
import asyncpg
import json
import logging
from typing import List, Union, Optional, Tuple

from disnake.ext import commands
from disnake import RawReactionActionEvent, Message

from bot import BotClient
from packages.utils.utils import EmbedColor, parse_args
import packages.utils.bot_sql as sql

EMOJIS = {
    "Zone 1": "<:h1:531458162931269653>",
    "Zone 2": "<:h2:531458184297054208>",
    "Zone 3": "<:h3:531458197962227723>",
    "Zone 4": "<:h4:531458216081620993>",
    "Zone 5": "<:h5:531458233387188254>",
    "Zone 6": "<:h6:531458252924518400>",
    "Zone 7": "<:h7:531458281609363464>",
    "Zone 8": "<:h8:531458309622988810>",
    "Zone 9": "<:h9:531458325368274956>",
    "Zone 10": "<:h10:531458344268070952>",
    "Super Troop": "<:super_troop:804932109428457492>",
    "Top-off": "<:topoff2:804926402234286091>",
    "Stop": "<:stop:531525166698594326>",
}

EXTRA_EMOJI = 3


class HappyDropdown(disnake.ui.Select):
    def __init__(self, bot: BotClient, emojis: List[str]):
        self.bot = bot
        self.emojis = emojis

        options = []
        for emoji in emojis:
            options.append(disnake.SelectOption(
                label=emoji,
                emoji=EMOJIS[emoji]))
        super().__init__(
            placeholder="Choose a donation zone...",
            min_values=1,
            max_values=len(options),
            options=options,
        )

    async def callback(self, inter: disnake.MessageInteraction):
        async with self.bot.pool.acquire() as con:
            sql = "SELECT * FROM happy WHERE message_id=$1"
            record = await con.fetchrow(sql, inter.message.id)

        print(dir(inter))
        print(inter.message.id)
        print(inter.id)
        print(inter.user)
        embed = await self.bot.inter_send(inter, panel="Hi",
                                          return_embed=True)
        await inter.response.edit_message(embed=embed[0][0])
        print(inter.message.id)
        return

        current_user = record["data"][payload.emoji.name]
        if current_user == payload.member.display_name:
            record["data"][payload.emoji.name] = None
        else:
            record["data"][payload.emoji.name] = payload.member.display_name

        await self._refresh_panel(record, message)
        await inter.response.edit_message(embed=embed[0][0])


class HappyView(disnake.ui.View):
    children: List[HappyDropdown]

    def __init__(self, bot: BotClient, panel_name: str, emojis: List[str],
                 rows: int):
        super().__init__()
        self.bot = bot
        self.panel_name = panel_name
        self.rows = rows

        self.add_item(HappyDropdown(bot, emojis))


class Happy(commands.Cog):

    def __init__(self, bot: BotClient):
        self.bot = bot
        self.pool = self.bot.pool
        self.log = logging.getLogger(f'{self.bot.settings.log_name}.Happy')
        self.emojis = EMOJIS

    @property
    def default_dataset(self) -> dict:
        """Return the default data parameter"""
        return {
            "Zone 1": None,
            "Zone 2": None,
            "Zone 3": None,
            "Zone 4": None,
            "Zone 5": None,
            "Zone 6": None,
            "Zone 7": None,
            "Zone 8": None,
            "Zone 9": None,
            "Zone 10": None,
            "Top-off": None,
            "Super Troop": None
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
                                          payload.channel_id,
                                          payload.guild_id)
        if not message:
            return

        # Reset the panel reaction
        await message.remove_reaction(payload.emoji, payload.member)

        # The panel should be active, but if it is not then clear the reactions
        # and update the db What to do when stop is called
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

    async def _refresh_panel(self,
                             record: Union[asyncpg.Record, dict],
                             message: Message,
                             reset_emojis=False,
                             kill: bool=False):
        panel, emoji_stack = self._panel_factory(record)
        embeds = await self.bot.send(ctx=None, description=panel,
                                     footnote=False, _return=True)
        for embed in embeds:
            if kill:
                await message.edit(embed=embed, view=None)
            else:
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

    async def _get_panel(self, panel_name: Union[str, None]
                         ) -> Optional[asyncpg.Record]:
        """
        Check to see if the given panel_name exits in the database. If it does
        then return the record for it.

        :param panel_name: Name of the panel to look up
        :return: The panel record ["panel_name", "panel_rows", "active",
        "message_id", "channel_id", "guild_id", "data"
        """
        async with self.bot.pool.acquire() as conn:
            sql = "SELECT * FROM happy WHERE panel_name=$1"
            return await conn.fetchrow(sql, panel_name)

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
                converter=lambda inter, panel_name: panel_name.title()),
    ) -> None:
        """
        Delete a panel from the /happy list

        Parameters
        ----------
        inter:
        panel_name: Name of panel to remove, use /happy list to find name
        """
        if not await self.panel_exists(panel_name):
            await self.bot.inter_send(inter,
                                      panel=f"Panel **{panel_name}** does not exist. Please use "
                                            f"`/happy list`",
                                      color=EmbedColor.WARNING)
            return

        async with self.bot.pool.acquire() as conn:
            sql = "DELETE FROM happy WHERE panel_name=$1"
            await conn.execute(sql, panel_name)

        await self.bot.inter_send(inter,
                                  panel=f'Deleted panel `{panel_name}`!',
                                  color=EmbedColor.SUCCESS)

    @happy.sub_command(
        name='create'
    )
    async def create_panel(self,
                           inter: disnake.ApplicationCommandInteraction,
                           panel_name: str,
                           row_count: commands.Range[1, 10]) -> None:
        """
        Create a new panel for donation requests
        Parameters
        ----------
        inter:
        panel_name: Name of the panel
        row_count: Number of rows to have, this can always be changed
        """
        panel_name = panel_name.title()
        if panel_name in await self.panel_name_autocmp(inter, panel_name):
            await self.bot.inter_send(inter,
                                      panel=f"Panel **{panel_name}** already exist. Please use "
                                            f"`/happy view`",
                                      color=EmbedColor.WARNING)
            return

        async with self.bot.pool.acquire() as conn:
            sql2 = f"""INSERT INTO happy (panel_name, panel_rows, active, 
            message_id, channel_id, guild_id, data) VALUES 
            ($1, $2, $3, $4, $5, $6, $7)"""

            await conn.execute(
                sql2,
                panel_name,
                row_count,
                False,
                0,
                0,
                0,
                self.default_dataset
            )
            await self.bot.inter_send(inter,
                                      panel=f'Panel `{panel_name}` created!',
                                      color=EmbedColor.SUCCESS)

    @happy.sub_command(
        name='list'
    )
    async def list_panels(self,
                          inter: disnake.ApplicationCommandInteraction) -> None:
        """
        View the created panels and their status
        """
        async with self.bot.pool.acquire() as conn:
            sql = """SELECT * FROM happy"""
            rows = await conn.fetch(sql)

        panel = f'{"NAME":<15} {"ROWS":<5} {"ACTIVE"}\n'
        for row in rows:
            active = "T" if row["active"] else "F"
            panel += f'{row["panel_name"]:<18} {row["panel_rows"]:<2} {active:<1}\n'
        await self.bot.send(inter, panel, code_block=True)

    @happy.sub_command(
        name='view'
    )
    async def view_panel(self,
                         inter: disnake.ApplicationCommandInteraction,
                         panel_name: str = commands.Param(converter=lambda inter, panel_name: panel_name.title())
                         ):
        """
        Activate the donation panel.

        Parameters
        ----------

        :param inter:
        :param panel_name: Name of the panel
        :return:
        """
        if not await self.panel_exists(panel_name):
            await self.bot.inter_send(
                inter,
                panel=f"Panel **{panel_name}** does not exist",
                color=EmbedColor.WARNING)
            return

        instance = await self._get_panel(panel_name)
        if not instance:
            return

        if instance["active"]:
            msg = f'Panel `{instance["panel_name"]}` is already open. ' \
                  f'Please close it first.'
            await self.bot.inter_send(inter, panel=msg,
                                      color=EmbedColor.WARNING)
            return

        # Cast the instance to a dict to enable writing
        instance = dict(instance)
        instance["active"] = True
        panel, emoji_stack = self._panel_factory(instance)

        view = HappyView(self.bot,
                         panel_name,
                         emoji_stack,
                         instance["panel_rows"])
        embed = await self.bot.inter_send(inter,
                                          panel=panel,
                                          flatten_list=True,
                                          return_embed=True)

        await inter.response.send_message(embed=embed[0], view=view)
        message = await inter.original_message()

        async with self.bot.pool.acquire() as conn:
            await conn.execute(sql.update_happy_panel(),
                               message.id,
                               True,
                               message.channel.id,
                               message.guild.id,
                               instance['panel_name'])

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

        instance = await self._get_panel(args["positional"])
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
    async def stop_panel(self,
                         inter: disnake.ApplicationCommandInteraction,
                         panel_name: str = commands.Param(converter=lambda inter, panel_name: panel_name.title())):

        instance = await self._get_panel(panel_name)
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
        await self._refresh_panel(instance, message, kill=True)
        await message.clear_reactions()
        await self.bot.inter_send(
            inter,
            panel="Stopped panel from running.",
            color=EmbedColor.SUCCESS)

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

        instance = await self._get_panel(string_objects[0])
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

        instance = await self._get_panel(instance["panel_name"])
        message = await self._get_message(instance["message_id"],
                                          instance["channel_id"],
                                          instance["guild_id"])
        await self.bot.send(ctx,
                            'Panel edited',
                            EmbedColor.SUCCESS,
                            footnote=False)
        if instance["active"]:
            await self._refresh_panel(instance, message, reset_emojis=True)

    def _panel_factory(self, instance: dict) -> Tuple[str, list]:
        """Parses the Record to create the content that is displayed and
        creates the emoji stack that associates with the amount of rows"""
        ranges = ['1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25',
                  '26 - 30', '31 - 35', '36 - 40',
                  '41 - 45', '46 - 50']

        data = instance["data"]
        emoji_stack = []

        status = 'Active' if instance["active"] else 'Inactive'
        panel = f'**Panel Name:**   `{instance["panel_name"]}`\n' \
                f'**Panel Status:** `{status}`\n\n'

        for i in range(0, instance["panel_rows"]):
            emoji = f"Zone {i + 1}"
            emoji_stack.append(emoji)
            panel += f'{self.emojis[emoji]} `[{ranges[i]:>7}]: {data[emoji] if data[emoji] else "":<20}`\n'

        panel += f'{self.emojis["Top-off"]} `[{"Top-off":>7}]: {data["Top-off"] if data["Top-off"] else "":<20}`\n'
        panel += f'{self.emojis["Super Troop"]} `[{"Super Troop":>7}]: {data["Super Troop"] if data["Super Troop"] else "":<20}`\n'
        emoji_stack.append("Top-off")
        emoji_stack.append("Super Troop")
        emoji_stack.append("Stop")

        return panel, emoji_stack

    @view_panel.autocomplete("panel_name")
    @delete_panel.autocomplete("panel_name")
    @stop_panel.autocomplete("panel_name")
    async def panel_name_autocmp(
            self,
            inter: Optional[disnake.ApplicationCommandInteraction],
            user_input: str) -> List[str]:
        """
        Autocomplete callback. To add this callback to a function add the
        decorator for the function.

        :param inter: Interaction
        :param user_input: The current input of the user
        :return: List of possible options based on the user input
        """

        async with self.pool.acquire() as conn:
            sql = "SELECT panel_name FROM happy"
            rows = await conn.fetch(sql)

        return [panel["panel_name"] for panel in rows if user_input.title()
                in panel["panel_name"]]

    async def panel_exists(self, panel_name: str) -> bool:
        """Wrapper for checking if the panel name is in the database"""
        if panel_name in await self.panel_name_autocmp(None, panel_name):
            return True
        return False


def title_str(inter: disnake.CommandInteraction, string: str) -> str:
    return string.title()


def setup(bot):
    bot.add_cog(Happy(bot))
