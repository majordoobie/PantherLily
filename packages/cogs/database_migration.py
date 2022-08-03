from discord.ext import commands
from discord import Member
from asyncpg import UniqueViolationError

from packages.utils.utils import *
from bot import BotClient
from database.migration import RecordObject
import sqlite3


class Migration(commands.Cog):
    """Run with migrate_donations off a couple times to populate the notes table"""
    def __init__(self, bot: BotClient):
        self.bot = bot

    @commands.check(is_owner)
    @commands.command()
    async def migrate_db(self, ctx):

        migrate_users = True
        migrate_donations = True

        db_file = 'database/livedatabase.db'
        db = sqlite3.connect(db_file)
        cur = db.cursor()

        if migrate_users:
            cur.execute('select * from MembersTable;')
            all_data = cur.fetchall()
            all_data.sort(key=lambda x: x[1].lower())

            await self.async_migrate_users(ctx=ctx, all_data=all_data)

        if migrate_donations:
            count = 0
            increment = 3000000
            while True:
                offset = count * increment
                print(f'Querying for data between {offset} - {offset + increment} records')

                cur.execute(f'''SELECT DonationsTable.increment_date, MembersTable.tag, DonationsTable.Current_Donation
                    FROM MembersTable, DonationsTable 
                    WHERE MembersTable.is_Active = 'True'
                    AND DonationsTable.increment_date > '2020-06-01'
                    ORDER BY DonationsTable.increment_date ASC
                    LIMIT {increment} OFFSET {offset}
                    ;''')
                donation_data = cur.fetchall()
                count += 1

                print("Converting string data to datetime...")

                if donation_data:
                    cleaned_up = [ [datetime.strptime(i[0],"%Y-%m-%d %H:%M:%S"),i[1],i[2]] for i in donation_data]
                    await self.async_migrate_donation(cleaned_up)

                else:
                    break

        cur.close()
        db.close()

    async def async_migrate_donation(self, donation_data):
        print("Committing dataset")
        sql = '''INSERT INTO clash_classic_update (increment_date, tag, current_donations) VALUES ($1, $2, $3)
                 ON CONFLICT DO NOTHING'''

        async with self.bot.pool.acquire() as con:
            try:
                await con.executemany(sql, donation_data)
            except UniqueViolationError as error:
                print(error)

        print("Done")


    async def async_migrate_users(self, ctx, all_data):
        # Fucking hack but whatever just needs to run once - there are some users that depend on other user so write them
        # a couple times to hopefully get the dependency down the db will handle integrity violations
        for i in range(0, 5):
            for record in all_data:
                if record[4] in [344958710885515264,344958710885515264, 205344025740312576, 178989365953822720, 318397249585545217,
                                 430922732658753559, 324681930807181335, 463684368452419584, 409465779965263882, 153732762896039936]:


                    record_obj = RecordObject(record)
                    try:
                        member = await get_discord_member(ctx, record_obj.discordid)
                    except:
                        member = None
                    await self.async_migrate_user(record_obj, member)

        for record in all_data:
            record_obj = RecordObject(record)
            try:
                member = await get_discord_member(ctx, record_obj.discordid)
            except:
                member = None
            await self.async_migrate_user(record_obj, member)


    async def async_migrate_user(self, record: RecordObject, member: Member):
        sql1 = '''INSERT INTO discord_user (discord_id, discord_name, discord_nickname, discord_discriminator, 
                  guild_join_date, global_join_date, db_join_date, in_zulu_base_planning, in_zulu_server, is_active) VALUES 
                  ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10) ON CONFLICT DO NOTHING'''

        sql2 = '''INSERT INTO clash_account (clash_tag, discord_id) VALUES ($1, $2) ON CONFLICT DO NOTHING'''

        sql3 = '''INSERT INTO user_note (discord_id, clash_tag, note_date, commit_by, note) VALUES 
                  ($1,$2,$3,$4,$5) ON CONFLICT DO NOTHING'''

        insert_tuple = (
            member.id if member else record.discordid,
            member.name if member else record.name,
            member.display_name if member else None,
            member.discriminator if member else None,
            member.joined_at if member else datetime.strptime(record.discord_joinedate, "%Y-%m-%d %H:%M:%S"),
            member.created_at if member else None,
            None,
            False,
            False,
            True if record.is_active == 'True' else False
        )
        clash_insert = (
            record.tag,
            member.id if member else record.discordid
        )

        async with self.bot.pool.acquire() as con:
            try:
                await con.execute(sql1, *insert_tuple)
            except Exception as error:
                import traceback
                exc = ''.join(traceback.format_exception(type(error), error, error.__traceback__, chain=True))
                print(exc)
            await con.execute(sql2, *clash_insert)
            if record.notes:
                note_records = []
                for note in record.notes:
                    note_records.append((
                        record.discordid,
                        record.tag,
                        note.date,
                        note.commit_by,
                        note.raw_note,
                    ))
                try:
                    await con.executemany(sql3, note_records)
                except:
                    pass


def get_note(record: RecordObject) -> tuple:
    return (
        record.discordid,
        record.tag,

    )


def setup(bot):
    bot.add_cog(Migration(bot))
