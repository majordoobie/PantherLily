from asyncpg import pool, Record
import json
import logging
from typing import Union, Optional, Tuple

from discord.ext import commands

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
            await self.bot.embed_print(ctx, "Please provide a panel name to delete. You can use the `Panther.Happy "
                                            "list` command to view all the panels available to you.",
                                       color=self.bot.WARNING)
            return None

        panel_name = panel_name.title()

        async with self.bot.pool.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )
            sql = f"""SELECT * FROM happy WHERE panel_name='{panel_name}' """
            row = await conn.fetchrow(sql)

        if not row:
            await self.bot.embed_print(ctx, f'Could not find a panel with the name of `{panel_name}`',
                                       color=self.bot.WARNING)
            return None

        else:
            return row

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload):
        pass

    @commands.group(
        aliases=['h'],
        invoke_without_command=True,
        brief='',
        description='Create and View interactive panels to volunteer for zones to donate to for war preparations.',
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
        await self.bot.embed_print(ctx, msg)

        msg = ''
        for k, v in self.emojis.items():
            if len(msg) > 1800:
                await ctx.send(msg)
                msg = ''
            msg += f'{k} {v}'
        await ctx.send(msg)
        msg = ''
        for emoji in self.bot.emojis:
            if len(msg)>1800:
                await ctx.send(msg)
                msg = ''
            msg += f'{emoji} {emoji.name} {emoji.id}\n'
        await ctx.send(msg)

    @happy.command(
        name='delete',
        aliases=['d'],
        brief='',
        help=''
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
        await self.bot.embed_print(ctx, f'Deleted panel `{panel_name["panel_name"]}`!', color=self.bot.SUCCESS)

    @happy.command(
        name='create',
        aliases=['c'],
        brief='',
        help=''
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
                await self.bot.embed_print(ctx, msg, color=self.bot.ERROR)
                return
            else:
                panel_rows = int(panel_rows)
                if not 1 <= panel_rows <=10:
                    msg = f'The number of rows you provided does not fall within 1 and 10.'
                    await self.bot.embed_print(ctx, msg, color=self.bot.ERROR)
                    return
        except ValueError:
            msg = f'Too many arguments provided. Args: `{args["positional"]}`\nCommand only takes 2. A name ' \
                  f'followed by the number of rows to populate.'
            await self.bot.embed_print(ctx, msg, color=self.bot.ERROR)
            self.log.error(f'{ctx.author.display_name} provided too many arguments to command: {args}')
            return

        async with self.bot.pool.acquire() as conn:
            await conn.set_type_codec(
                'json',
                encoder=json.dumps,
                decoder=json.loads,
                schema='pg_catalog'
            )
            sql = f"""SELECT panel_name FROM happy WHERE panel_name='{panel_name}' """
            sql2 = f"""INSERT INTO happy (panel_name, panel_rows, active, message_id, data) VALUES 
            ($1, $2, $3, $4, $5)"""

            if await conn.fetchrow(sql):
                await self.bot.embed_print(ctx, f'Panel `{panel_name}` already exists.', color=self.bot.WARNING)
            else:

                await conn.execute(
                    sql2,
                    panel_name,
                    panel_rows,
                    False,
                    0,
                    {
                        1: None,
                        2: None,
                        3: None,
                        4: None,
                        5: None,
                        6: None,
                        7: None,
                        8: None,
                        9: None,
                        10: None,
                        "top": None,
                        "super": None
                    }
                )
                await self.bot.embed_print(ctx, f'Panel `{panel_name}` created!', color=self.bot.SUCCESS)

    @happy.command(
        name='view',
        aliases=['v'],
        brief='',
        help=''
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

        panel, emoji_stack = self._panel_factory(instance)
        embed = await self.bot.embed_print(ctx, panel, footnote=False, _return=True)
        panel = await ctx.send(embed=embed)
        for emoji in emoji_stack:
            await panel.add_reaction(emoji)

        async with self.bot.pool.acquire() as conn:
            sql = f"""UPDATE happy SET message_id={panel.id} WHERE panel_name='{instance["panel_name"]}' """
            await conn.execute(sql)

    @happy.command(
        name='list',
        aliases=['l'],
        brief='',
        help=''
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

        panel = f'{"name":<10} {"#":<2} {"active":<5}\n'
        for row in rows:
            active = "True" if row["active"] else "False"
            panel += f'{row["panel_name"]:<10} {row["panel_rows"]:<2} {active:<5}\n'
        await self.bot.embed_print(ctx, panel, codeblock=True)

    def _panel_factory(self, instance) -> Tuple[str, list]:
        ranges = ['1 - 5', '6 - 10', '11 - 15', '16 - 20', '21 - 25', '26 - 30', '31 - 35', '36 - 40',
                  '41 - 45', '46 - 50']

        data = instance["data"]
        emoji_stack = []

        panel = f'Panel: **{instance["panel_name"]}**\n'
        for i in range(0, instance["panel_rows"]):
            emoji = self.emojis[f'h{i + 1}']
            emoji_stack.append(emoji)
            key = f'{i+1}'
            panel += f'{emoji} `[{ranges[i]:>7}]: {data[key] if data[key] else "":<20}`\n'

        panel += f'{self.emojis["topoff2"]} `[{"Top off":>7}]: {data["top"] if data["top"] else "":<20}`\n'
        panel += f'{self.emojis["super_troop"]} `[{"Super":>7}]: {data["super"] if data["super"] else "":<20}`\n'
        emoji_stack.append(self.emojis["topoff2"])
        emoji_stack.append(self.emojis["super_troop"])
        emoji_stack.append(self.emojis["stop"])

        return panel, emoji_stack




def setup(bot):
    bot.add_cog(Happy(bot))
