import sqlite3
import re
from datetime import datetime
from discord import member

import psycopg2
#from packages.private.secrets import *
from secrets import *

var = {
       'Goku': 344958710885515264,
       'SgtMajorDoobie': 344958710885515264,
       'Sgt': 344958710885515264,
       'Goku⁹⁰⁰⁰': 344958710885515264,
       'zig': 178989365953822720,
       'Chadwick': 318397249585545217,
       'Zag-geek': 205344025740312576,
       'Felicia': 430922732658753559,
       'Superman': 324681930807181335,
       'JosiahDH': 463684368452419584,
       'fra': 409465779965263882
       }

RE_STRING = r'\[(\d+)-(\w+)-(\d+)(\W)(\d+):(\d+)\]'

class RecordObject:
    def __init__(self, record):
        self.record = record
        self.objectfy()

    def __str__(self):
        return f'{self.tag} {self.discordid}'

    def objectfy(self):
        self.tag = self.record[0]
        self.name = self.record[1]
        self.townhall = self.record[2]
        self.league = self.record[3]
        self.discordid = self.record[4]
        self.discord_joinedate = self.record[5]
        self.in_planning = self.record[6]
        self.is_active = self.record[7]
        self.notes = sepearate_notes(self.record[8])

class NoteObject:
    def __init__(self, note):
        self.note = note
        self.objectfy()

    def objectfy(self):
        self.date = datetime.strptime(self.note[1:18], '%d-%b-%Y %H:%M')
        self.commit_by = var[self.note.split('\n')[1].split(' ')[2]]
        self.raw_note = 'Migrated from PantherLily2:\n' + '\n'.join(self.note.split('\n')[2:])

def sepearate_notes(record):
    """Break down the notes string into a list of notes"""
    if record == '' or None:
        return

    ranges = {}
    last = 0
    notes = []

    # Iterate over the matches and fill in the dict with the ranges in the string to get the note from
    for index, match in enumerate(re.finditer(RE_STRING, record)):
        ranges[index] = [match.start(), 0]
        if (index - 1) == -1:
            continue
        ranges[index - 1][1] = (match.start() - 1)
        last = index

    ranges[last][1] = -1

    # Use the ranges created to slice the note string
    for note in range(0, (last + 1)):
        range_set = ranges[note]
        if range_set[1] == -1:
            note = NoteObject(record[range_set[0]:])
        else:
            note = NoteObject(record[range_set[0]:range_set[1]])

        notes.append(note)

    return notes


def get_users(all_data):
    users = {}
    for record in all_data:
        notes = sepearate_notes(record[8])
        for note in notes:
            user = note.split('\n')[1].split(' ')[2]
            if user not in users.keys():
                users[user] = 1
            else:
                users[user] +=1

    print(users)

def migrate_note(db_obj: RecordObject, conn):

    sql = """INSERT INTO user_note (discord_id, clash_tag, note_date, commit_by, note) VALUES (%s, %s, %s, %s, %s)"""
    with conn.cursor() as cur:
        for note in db_obj.notes:
            note: NoteObject
            insert_tuple = (
                db_obj.discordid,
                db_obj.tag,
                note.date,
                note.commit_by,
                note.raw_note
            )
            cur.execute(sql, insert_tuple)

def migrate_user(record: RecordObject, member: member):
    sql1 = """INSERT INTO discord_user (discord_id, discord_name, discord_nickname, discord_discriminator, guild_join_date, 
    global_join_date, db_join_date, in_zulu_base_planning, in_zulu_server, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    sql2 = """INSERT INTO clash_account (clash_tag, discord_id) VALUES (%s, %s)"""

    insert_tuple = (
        member.id if member else record.discordid,
        member.name if member else record.name,
        member.display_name if member else None,
        member.discriminator if member else None,
        member.joined_at if member else record.discord_joinedate,
        member.created_at if member else None,
        None,
        False,
        False,
        record.is_active
    )
    clash_insert = (
        record.tag,
        member.id if member else record.discordid
    )

    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
    )

    with conn.cursor() as cur:
        try:
            cur.execute(sql1, insert_tuple)
        except psycopg2.IntegrityError:
            conn.rollback()

        try:
            cur.execute(sql2, clash_insert)
        except psycopg2.IntegrityError as error:
            conn.rollback()
            print(error)
        try:
            if record.notes:
                migrate_note(record, conn)
        except psycopg2.IntegrityError as error:
            conn.rollback()
            print(error)

        conn.commit()

    conn.close()

def migrate_donation(record_tuple):
    # Commit to new db would go here

    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
    )

    with conn.cursor() as cur:
        # sql = """INSERT INTO user_note (discord_id, clash_tag, note_date, commit_by, note) VALUES (%s, %s, %s, %s, %s)"""
        sql = '''INSERT INTO clash_classic_update (increment_date, tag, current_donations) VALUES (%s, %s, %s)'''
        try:
            cur.executemany(sql, record_tuple)
            conn.commit()
        except psycopg2.IntegrityError:
            conn.rollback()
def
def main():
    """main for testing, run it in the bot for discord access"""
    db_file = 'livedatabase.db'
    db = sqlite3.connect(db_file)
    cur = db.cursor()

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
            cur.close()
            break

    db.close()





    # cur.execute("select * from MembersTable;")
    # global all_data
    # all_data = cur.fetchall()
    # cur.close()
    # db.close()
    # db_objects = []
    # for record in all_data:
    #     #migrate_user(RecordObject(record))
    #     db_objects.append(RecordObject(record))
    #
    # print(db_objects)



if __name__ == '__main__':
    main()


