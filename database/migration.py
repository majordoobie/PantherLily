import sqlite3
import re
from datetime import datetime

import psycopg2
from packages.private.secrets import *

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
        self.raw_note = 'Migrated from PantherLily2:\n\n' + self.note.split('\n')[2]


def sepearate_notes(record):
    """Break down the notes string into a list of notes"""
    if record == '':
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
        note = NoteObject(record[ranges[note][0]:ranges[note][1]])
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

def migrate_note(db_obj: RecordObject):
    conn = psycopg2.connect(
        dbname=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD,
        host=POSTGRES_HOST,
    )

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
            print(insert_tuple)
            cur.execute(sql, insert_tuple)
        conn.commit()
    conn.close()

def migrate_user(record: RecordObject):
    sql = """INSERT INTO discord_user (discord_id, discord_name, discord_nickname, discord_discriminator, guild_join_date, 
    global_join_date, db_join_date, in_zulu_base_planning, in_zulu_server, is_active) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""

    insert_tuple = (
        record.discordid,
        record.name,

    )


def main():
    db_file = 'database/livedatabase.db'
    db = sqlite3.connect(db_file)
    cur = db.cursor()
    cur.execute('select * from MembersTable;')
    global all_data
    all_data = cur.fetchall()
    cur.close()
    db.close()
    db_objects = []
    for record in all_data:
        #migrate_user(RecordObject(record))
        db_objects.append(RecordObject(record))

    print(db_objects)












if __name__ == '__main__':
    main()
