from discord.ext import commands
import logging

from database.migration import migrate_donation
from packages.cogs.utils.utils import *
from bot import BotClient
from packages.database_schema import drop_tables
from database.migration import RecordObject, NoteObject, migrate_user
import sqlite3


class Migration(commands.Cog):
    """Run with migrate_donations off a couple times to populate the notes table"""
    def __init__(self, bot: BotClient):
        self.bot = bot

    @commands.check(is_owner)
    @commands.command()
    async def migrate_db(self, ctx):

        migrate_users = False
        migrate_donations = True

        db_file = 'database/livedatabase.db'
        db = sqlite3.connect(db_file)
        cur = db.cursor()

        if migrate_users:
            cur.execute('select * from MembersTable;')
            all_data = cur.fetchall()
            all_data.sort(key=lambda x: x[1].lower())
            record_object_list = []

            for record in all_data:
                if record[1].startswith('Sgt') or record[1].startswith('Goku') or record[1].startswith('Zag'):
                    record_obj = RecordObject(record)
                    try:
                        member = await get_discord_member(ctx, record_obj.discordid)
                    except:
                        member = None
                    migrate_user(record_obj, member)
                else:
                    record_object_list.append(RecordObject(record))

            var = {
                'Goku': 344958710885515264,
                'SgtMajorDoobie': 344958710885515264,
                'Sgt': 344958710885515264,
                'Goku⁹⁰⁰⁰': 344958710885515264,
                'zig': 178989365953822720,
                'Chadwick': 318397249585545217,
                'Zag-geek': 205344025740312576,
                'Zag': 205344025740312576,
                'Felicia': 430922732658753559,
                'Superman': 324681930807181335,
                'JosiahDH': 463684368452419584,
                'fra': 409465779965263882,
                'President': 153732762896039936,
            }
            for record_obj in record_object_list:
                if record_obj.name in var.keys():
                    try:
                        member = await get_discord_member(ctx, record_obj.discordid)
                    except:
                        member = None
                    migrate_user(record_obj, member)


            for record_obj in record_object_list:
                try:
                    member = await get_discord_member(ctx, record_obj.discordid)
                except:
                    member = None
                migrate_user(record_obj, member)

                # record_object_batchs.append(RecordObject(record))
                # try:
                #     member = await get_discord_member(ctx, record_obj.discordid)
                # except:
                #     member = None
                # migrate_user(record_obj, member)

        if migrate_donations:
            count = 0
            while True:
                offset = count * 3000000
                print(offset)

                cur.execute(f'''SELECT DonationsTable.increment_date, MembersTable.tag, DonationsTable.Current_Donation
                    FROM MembersTable, DonationsTable WHERE MembersTable.is_Active = 'True'
                    ORDER BY DonationsTable.increment_date ASC
                    LIMIT 3000000 OFFSET {offset}
                    ;''')

                donation_data = cur.fetchall()

                if donation_data:
                    migrate_donation(donation_data)
                    count += 1
                else:
                    break

        cur.close()
        db.close()





def setup(bot):
    bot.add_cog(Migration(bot))
