import asyncio
import logging
import traceback
from typing import Tuple

import coc.utils
from disnake.ext import commands

from bot import BotClient
from packages.utils import bot_sql as sql
from packages.utils.paginator import Paginator
from packages.utils.utils import *


class ViewNotes(disnake.ui.View):
    def __init__(self, bot: BotClient,
                 inter: disnake.ApplicationCommandInteraction,
                 member: disnake.Member):
        super().__init__()
        self.bot = bot
        self.member = member
        self.inter = inter

    @disnake.ui.button(label="View Users Notes",
                       style=disnake.ButtonStyle.green)
    async def confirm(self,
                      button: disnake.ui.Button,
                      inter: disnake.MessageInteraction):

        async with self.bot.pool.acquire() as conn:
            note_records = await conn.fetch(sql.select_user_notes(),
                                            self.member.id)

        await inter.response.edit_message(view=None)
        if not note_records:
            embed = await self.bot.inter_send(
                inter,
                panel="User does not have any notes",
                return_embed=True,
                flatten_list=True)
            await inter.send(embed=embed[0])
            self.stop()
            return

        notes = []
        for note in note_records:
            try:
                player = await self.bot.coc_client.get_player(
                    note["clash_tag"])
            except:
                player = None

            try:
                commit_by = self.bot.get_user(note["commit_by"])
            except:
                commit_by = None

            clash_player = player.name if player else note["clash_tag"]
            clash_tag = note["clash_tag"]

            commit_by_name = commit_by.display_name if commit_by else note[
                "commit_by"]

            date = note["note_date"].strftime("%Y-%m-%d %H:%M")

            notes.append(
                f"`{'Player:':<11}{clash_player}`\n"
                f"`{'Commit By:':<11}{commit_by_name}`\n"
                f"`{'Tag:':<11}{clash_tag}`\n"
                f"`{'Date:':<11}{date}`\n\n"
                f"{note['note']}"
            )

        embeds = await self.bot.inter_send(inter, panels=notes,
                                           return_embed=True,
                                           flatten_list=True)
        view = Paginator(embeds, 3)
        await inter.send(embeds=view.embed, view=view)
        view.message = await inter.original_message()
        self.stop()


class Leaders(commands.Cog):
    def __init__(self, bot: BotClient):
        self.bot = bot
        self.log = logging.getLogger(f"{self.bot.settings.log_name}.Leaders")

    async def _get_updates(self, member_id: int) -> Tuple[
        asyncpg.Record, List[asyncpg.Record]]:
        """Method gets the most up to date user information - this code is
        repeated a lot in this class """
        async with self.bot.pool.acquire() as con:
            db_discord_member = await con.fetchrow(
                sql.select_discord_user_id(), member_id)

            db_clash_accounts = await con.fetch(
                sql.select_clash_account_discord_id(), member_id)

        return db_discord_member, db_clash_accounts

    async def _enable_user(
            self,
            conn: asyncpg.Connection,
            inter: disnake.ApplicationCommandInteraction,
            msg: str,
            member: disnake.Member,
            player: coc.Player
    ) -> None:
        """Common task for setting a users information when being
        registered"""

        db_member, db_accs = await self._get_updates(member.id)
        panel = _get_account_panel(db_member, db_accs, msg)

        await conn.execute(sql.insert_user_note(),
                           member.id,
                           player.tag,
                           datetime.now(),
                           inter.author.id,
                           panel)

        self.log.error(panel)

        await self.bot.inter_send(inter, panel=panel, color=EmbedColor.SUCCESS)

        await self._set_defaults(inter, member,
                                 player.town_hall,
                                 player.name)

    async def _multi_account_logic(
            self,
            inter: disnake.ApplicationCommandInteraction,
            coc_record: tuple,
            member: disnake.Member,
            player: coc.Player,
            set_alternate: bool) -> None:
        """Repeated code in add_user"""
        async with self.bot.pool.acquire() as con:
            db_member, db_cocs = await self._get_updates(member.id)
            if not set_alternate:
                msg = _get_alternate_warning_panel(db_member, db_cocs)
                self.log.error(msg)
                await self.bot.inter_send(inter, panel=msg,
                                          title="Multiple clash accounts",
                                          color=EmbedColor.WARNING)
                return
                # if the user added the flag then add the new clash account
                # and set it to primary
            else:
                for db_acc in db_cocs:
                    if db_acc["clash_tag"] == player.tag:
                        if db_acc["is_primary_account"]:
                            await self.bot.inter_send(inter,
                                                      panel=f"Clash [{player.tag}] is already set to primary",
                                                      title="No action taken",
                                                      color=EmbedColor.WARNING)
                            return

                await con.execute(sql.update_discord_user_names(),
                                  member.id,
                                  member.name,
                                  member.discriminator,
                                  player.name
                                  )

                await con.execute(sql.update_discord_user_activity_only(),
                                  True,
                                  member.id)

                await con.execute(sql.update_clash_account_coc_alt_cascade(),
                                  False,
                                  member.id)

                new_coc = True
                for coc_record in db_cocs:
                    if coc_record["clash_tag"] == coc_record[0]:
                        new_coc = False

                if new_coc:
                    await con.execute(sql.insert_clash_account(), *coc_record)
                else:
                    await con.execute(
                        sql.update_clash_account_coc_alt_primary(),
                        True, member.id, player.tag)

                await self._remove_defaults(member)
                await self._set_defaults(
                    inter,
                    member,
                    player.town_hall,
                    player.name
                )

                await self._enable_user(
                    con,
                    inter,
                    "Alternate clash account set",
                    member,
                    player
                )

    async def _set_defaults(self,
                            inter: disnake.ApplicationCommandInteraction,
                            member: disnake.Member,
                            clash_level: int,
                            in_game_name: str) -> None:
        """Set default roles and name change"""
        default_roles = get_default_roles(inter.guild,
                                          self.bot.settings,
                                          clash_level)

        if default_roles is None:
            msg = f"Unable to retrieve `th{clash_level}s` role or `CoC " \
                  f"Members` role. please make sure it " \
                  f"exits for me to automatically assign it to users."
            await self.bot.inter_send(inter, panel=msg, title="Role not found",
                                      color=EmbedColor.ERROR)
        else:
            try:
                await member.add_roles(*default_roles)
                for role in default_roles:
                    self.bot.log_role_change(member, role, log=self.log)
            except Exception as error:
                self.bot.log.error(error, exc_info=True)
                exc = "".join(traceback.format_exception(type(error), error,
                                                         error.__traceback__,
                                                         chain=True))
                await self.bot.inter_send(inter, panel=exc,
                                          title="User role change error",
                                          color=EmbedColor.ERROR)

        try:
            if member.display_name != in_game_name:
                old_name = member.display_name
                await member.edit(nick=in_game_name, reason="Panther Bot")
                self.log.error(
                    f"Changed `{old_name}` name to `{in_game_name}`")
        except Exception as error:
            self.bot.log.critical(error, exc_info=True)
            exc = "".join(traceback.format_exception(type(error), error,
                                                     error.__traceback__,
                                                     chain=True))
            await self.bot.inter_send(inter, panel=exc,
                                      title="Unable to change users nickname",
                                      color=EmbedColor.ERROR)

    async def _remove_defaults(self, member: disnake.member) -> None:
        """
        Function used to remove the default roles
        Parameters
        ----------
        member: Member
            Member object representing the user to affect
        """
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

    async def _remove_user(self, ctx, member_id, clash_tag,
                           return_msg: bool = False, kick_message=None):
        async with self.bot.pool.acquire() as con:

            await con.execute(sql.update_discord_user_activity_only(), False,
                              member_id)

            await con.execute(sql.update_clash_account_coc_alt_primary(),
                              False, member_id, clash_tag)

            db_member, db_coc = await self._get_updates(member_id)
            if kick_message:
                msg = _get_account_panel(db_member,
                                         db_coc,
                                         f"__**Kick Message:**__\n{kick_message}")
            else:
                msg = _get_account_panel(db_member, db_coc,
                                         "User set to inactive")
            self.log.error(msg)
            await con.execute(sql.insert_user_note(), member_id, clash_tag,
                              datetime.now(), ctx.author.id, msg)

            if return_msg:
                return msg
            else:
                await self.bot.inter_send(ctx,
                                          panel=msg,
                                          color=EmbedColor.SUCCESS)

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        name="remove_user",
        dm_permission=False,
    )
    async def remove(self,
                     inter: disnake.ApplicationCommandInteraction,
                     member: disnake.Member = None,
                     player: Optional[str] = None,
                     set_message: bool = True):
        """
        Remove user from Pantherlily. Set the "set_message" to False to avoid
        having to submit a message

        Parameters
        -----------

        member: Member is the discord mention of the user
        player: Any data attribute; coc_tag, discord_id, nick, etc
        set_message: Set False to prevent modal from opening
        """

        if player is None and member is None:
            await self.bot.inter_send(inter,
                                      panel="**Player** or **Member** option must be used",
                                      title="Option Missing",
                                      color=EmbedColor.ERROR)
            return

        # Get the database user object
        db_member: asyncpg.Record
        query = member.id if member else player
        try:
            db_member = await get_database_user(query, self.bot.pool)
        except RuntimeError as error:
            records: Record = error.args[-1]
            discord_id = records[0]["discord_id"]
            # Check if there is multiple results of different users
            for record in records:
                if record["discord_id"] != discord_id:
                    users = [(record["discord_id"], record["discord_name"],)
                             for record in records]
                    users_string = ""
                    for _tuple in users:
                        users_string += f"{_tuple}\n"

                    msg = f"Query returned multiple discord_ids. " \
                          f"Try using a different query term to attempt to " \
                          f"resolve. Otherwise, let doobie know about " \
                          f"this issue.\n{users_string}"

                    await self.bot.inter_send(inter, panel=msg,
                                              title="Multiple Results",
                                              color=EmbedColor.WARNING)
                    return
            db_member = records[0]

        if db_member is None:
            await self.bot.inter_send(inter,
                                      panel=f"Database user [{query}] was not found",
                                      title="User not found",
                                      color=EmbedColor.WARNING)
            return

        # Fetch all the clash account
        clash_tag = None
        async with self.bot.pool.acquire() as con:
            clash_accounts = await con.fetch(
                sql.select_clash_account_discord_id(), db_member["discord_id"])

        # Fetch the primary account
        for clash_account in clash_accounts:
            if clash_account["is_primary_account"]:
                clash_tag = clash_account["clash_tag"]
        if not clash_tag:
            clash_tag = clash_accounts[0]["clash_tag"]

        # If database user object exists, then
        # attempt to get the discord member object
        member = await get_discord_member(inter,
                                          db_member["discord_id"],
                                          self.bot.inter_send, _return=True)

        if set_message:
            await inter.response.send_modal(
                title="Kick Message",
                custom_id="kick_message",
                components=[
                    disnake.ui.TextInput(
                        label="Kick Message",
                        placeholder="Leave blank to omit kick message",
                        custom_id="kick_message_text",
                        style=disnake.TextInputStyle.paragraph,
                    )
                ]
            )

            try:
                modal_inter: disnake.ModalInteraction = await self.bot.wait_for(
                    "modal_submit",
                    check=lambda
                        x: x.custom_id == "kick_message" and x.author.id == inter.author.id,
                    timeout=300
                )
            except asyncio.TimeoutError:
                return

            msg = await self._remove_user(
                inter,
                db_member["discord_id"],
                clash_tag,
                return_msg=True,
                kick_message=modal_inter.text_values.get("kick_message_text"))

            embeds = await self.bot.inter_send(inter, panel=msg,
                                               return_embed=True)
            await modal_inter.response.send_message(embeds=embeds[0])

        else:
            await self._remove_user(inter, db_member["discord_id"], clash_tag)

        if member:
            await self._remove_defaults(member)

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        name="add_user",
        dm_permission=False,
    )
    async def add(
            self,
            inter: disnake.ApplicationCommandInteraction,
            member: disnake.Member,
            clash_tag: str,
            set_alternate: bool = False
    ) -> None:
        """
        Register a user or set a new Clash of Clans alternate

        Parameters
        ----------

        :param clash_tag:
        :param set_alternate:
        :param inter:
        :param member:
        :return:
        """
        # Get the coc player object. If it fails it will print a message
        player = await get_coc_player(inter,
                                      clash_tag,
                                      self.bot.coc_client,
                                      self.bot.inter_send)
        if not player or not member:
            return

        discord_record = (
            member.id,
            member.name,
            member.display_name,
            member.discriminator,
            member.joined_at,
            member.created_at,
            datetime.now(),
        )
        coc_record = (
            player.tag,
            member.id,
        )
        """
        ['discord_id', 'discord_name', 'discord_nickname', 
        'discord_discriminator', 'guild_join_date', 'global_join_date', 
        'db_join_date', 'in_zulu_base_planning', 'in_zulu_server', 'is_active']
        
        ['clash_tag', 'discord_id', 'is_primary_account'] 
        """

        async with self.bot.pool.acquire() as con:
            # Attempt to pull data for that user
            db_member, db_accs = await self._get_updates(member.id)

            # Add a brand-new user that is not in the database at all
            if db_member is None and len(db_accs) == 0:
                self.log.error(f"Adding new user {member.name} "
                               f"with clash of {player.tag}")

                await con.execute(sql.insert_discord_user(), *discord_record)
                await con.execute(sql.insert_clash_account(), *coc_record)

                await self._enable_user(con,
                                        inter,
                                        "New user added",
                                        member,
                                        player)

            # If user HAS a discord account BUT their
            # active state is set to false
            elif not db_member["is_active"]:
                self.log.error(f"Discord member `{member.name}:{member.id}` "
                               f"already exists, but `is_active` "
                               f"attribute is set to `false`. Attempting to "
                               f"enable")

                # Check if the clash account is already there
                new_account = True
                msg = "User enabled"
                for db_acc in db_accs:
                    if db_acc["clash_tag"] == player.tag:
                        new_account = False
                        await con.execute(
                            sql.update_clash_account_coc_alt_primary(),
                            True,
                            member.id,
                            player.tag
                        )

                if new_account:
                    try:
                        await con.execute(sql.insert_clash_account(),
                                          *coc_record)
                    except asyncpg.UniqueViolationError as err:
                        msg = str(err) + "\n\nClash tag already exists. If " \
                                         "you still want to assign this tag " \
                                         "then you must delete the tag first " \
                                         "with **/delete_clash_account**"
                        await self.bot.inter_send(inter, panel=msg,
                                                  title="Unique Key Violation Error",
                                                  color=EmbedColor.ERROR)
                        return

                    msg = "New clash account added"

                await update_active_user(member, con, True)
                await self._enable_user(con,
                                        inter,
                                        msg,
                                        member,
                                        player)


            elif db_member["is_active"]:
                if len(db_accs) == 0:
                    await con.execute(sql.insert_clash_account(), *coc_record)

                    await self._enable_user(
                        con,
                        inter,
                        "Clash account assigned",
                        member,
                        player
                    )

                elif len(db_accs) == 1:
                    if db_accs[0]["clash_tag"] == player.tag:
                        if db_accs[0]["is_primary_account"]:
                            msg = _get_account_panel(db_member,
                                                     db_accs,
                                                     "No action taken")
                            self.log.error(msg)
                            await self.bot.inter_send(inter, panel=msg)

                        else:
                            await con.execute(
                                sql.update_clash_account_coc_alt_primary(),
                                True, member.id, player.tag)
                            await self._enable_user(
                                con,
                                inter,
                                "Clash account set",
                                member,
                                player
                            )
                    else:
                        await self._multi_account_logic(inter,
                                                        coc_record,
                                                        member,
                                                        player,
                                                        set_alternate)

                elif len(db_accs) > 1:
                    await self._multi_account_logic(inter,
                                                    coc_record,
                                                    member,
                                                    player,
                                                    set_alternate)

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        name="delete_clash_account",
        dm_permission=False
    )
    async def del_coc(self,
                      inter: disnake.ApplicationCommandInteraction,
                      clash_tag: str) -> None:
        """
        Remove a clash tag from the database allowing the tag to be linked
        with another user.

        Parameters
        -----------

        inter:
        clash_tag: The tag to remove
        """

        clash_tag = coc.utils.correct_tag(clash_tag)
        if not coc.utils.is_valid_tag(clash_tag):
            await self.bot.inter_send(inter,
                                      title=f"[{clash_tag}] is an invalid tag",
                                      color=EmbedColor.ERROR)
            return

        conn: asyncpg.Pool
        async with self.bot.pool.acquire() as conn:
            try:
                await conn.execute(sql.delete_clash_account_record(),
                                   clash_tag)
                await self.bot.inter_send(inter,
                                          panel=f"Deleted [{clash_tag}]",
                                          color=EmbedColor.SUCCESS)
            except Exception as error:
                await self.bot.inter_send(inter, panel=str(error),
                                          title="Unknown error",
                                          color=EmbedColor.ERROR)

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        name="view",
        dm_permission=False
    )
    async def view(
            self,
            inter: disnake.ApplicationCommandInteraction,
            member: disnake.Member = commands.Param(lambda inter: inter.author)
    ) -> None:
        """
        Display the users current enrollment status. Additionally, view the
        users notes

        Parameters
        -----------
        inter:
        member: Member to display information of
        """

        payload = await self._get_updates(member.id)
        if not any(payload):
            await self.bot.inter_send(
                inter,
                panel=f"Could not find any data for **{member.display_name}** "
                      f"in the database.",
                color=EmbedColor.WARNING
            )
            return

        db_member, db_cocs = payload
        msg = _get_account_panel(db_member, db_cocs)
        await self.bot.inter_send(inter, panel=msg,
                                  color=EmbedColor.SUCCESS,
                                  view=ViewNotes(self.bot, inter, member))

    @commands.check(is_leader)
    @commands.slash_command(
        auto_sync=True,
        name="report",
        dm_permission=False,
    )
    async def report(self,
                     inter: disnake.ApplicationCommandInteraction,
                     weeks: int = 1) -> None:
        """
        Show the donation report of all users in the clan. By default only
        one week is shown.

        Parameters
        ----------
        weeks: Number of weeks to show. By default, it is one week.
        """

        true = self.bot.settings.emojis["true"]
        false = self.bot.settings.emojis["false"]
        warning = "<:warning:807778609825447968>"

        # Get the amount of weeks to pull back
        dates = []
        current_week = get_utc_monday()
        for i in range(0, weeks):
            dates.append(get_utc_monday() - timedelta(days=(i * 7)))

        # Get report blocks based on dates
        reports = []
        async with self.bot.pool.acquire() as con:
            for date in dates:
                players = await con.fetch(
                    sql.select_classic_view().format(date))
                players.sort(key=lambda x: x["donation_gains"], reverse=True)
                legend = f"{true} User met weekly quota\n"
                legend += f"{false} User has yet to meet quota\n"
                legend += f"{warning} User is exempt from quota\n\n"
                data_block = f"`{self.bot.space * 3}{'Player':<14}{self.bot.space}{'Donation'}`\n"
                for player in players:
                    donation = player["donation_gains"]
                    emoji = true if donation >= 300 else false
                    if date == current_week:
                        if not player["guild_join_date"] < current_week:
                            emoji = warning
                    data_block += f"{emoji}{self.bot.space}`" \
                                  f"{player['clash_name']:<17.17}`{self.bot.space}`{donation:>5}`\n"

                embed = await self.bot.inter_send(
                    inter,
                    panels=[legend, data_block],
                    title=f"Week of: {date.strftime('%Y-%m-%d')} (GMT)",
                    return_embed=True,
                    flatten_list=True
                )
                reports.append(embed[0])
                reports.append(embed[1])

        view = Paginator(reports, 2)
        await inter.send(embeds=view.embed, view=view)
        view.message = await inter.original_message()

def _get_account_panel(discord_member: asyncpg.Record,
                       coc_accounts: List[asyncpg.Record],
                       title: str = "") -> str:
    """
    Create the panel that is used to confirmed that the leader action has
    completed like a user was added, modified or removed.

    :param discord_member: db discord record
    :param coc_accounts: List of db coc records
    :param title: Optional string to print
    :return: Formatted string to print
    """

    coc_panel = f"`{'Clash Tag':<15}` `{'Primary Acc':<15}`\n"
    for coc_account in coc_accounts:
        coc_bool = "True" if coc_account["is_primary_account"] else "False"
        coc_panel += f"`{coc_account['clash_tag']:<15}` `{coc_bool:<15}`\n"

    if coc_panel == "":
        coc_panel = "No CoC Accounts Bound"

    base = f"__Player Account__\n" \
           f"`{'Discord Nick:':<14}` `{discord_member['discord_nickname']}`\n" \
           f"`{'Discord Name:':<14}` `{discord_member['discord_name']}`\n" \
           f"`{'Is Active:':<14}` `{discord_member['is_active']}`\n" \
           f"\n__Clash Accounts__:\n" \
           f"{coc_panel}"

    if title == "":
        return base
    else:
        return f"{title}\n\n{base}"


def _get_alternate_warning_panel(discord_member: asyncpg.Record,
                                 coc_accounts: List[asyncpg.Record]) -> str:
    """Return a formatted string for warning user about an already existing
    account"""
    title = f"User `{discord_member['discord_name']}` already has a clash " \
            f"account. If you would like to set an alternate then please " \
            f"ass the **set_alternate** flag"
    return _get_account_panel(discord_member, coc_accounts, title)


async def insert_discord_record(discord_record: tuple,
                                conn: asyncpg.Connection) -> None:
    await conn.execute(sql.insert_discord_user(), *discord_record)


async def insert_coc(coc_record: tuple,
                     conn: asyncpg.Connection) -> None:
    await conn.execute(sql.insert_clash_account(), *coc_record)


async def update_active_user(member: disnake.Member, conn: asyncpg.Connection,
                             active: bool) -> None:
    await conn.execute(
        sql.update_discord_user_set_active(),
        active,
        member.name,
        member.discriminator,
        member.display_name,
        datetime.utcnow(),
        member.id
    )


def setup(bot):
    bot.add_cog(Leaders(bot))
