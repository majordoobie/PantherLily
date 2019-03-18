import sqlite3
import datetime

class ZuluDB:
    def __init__(self, db):
        """
        Class used to connect to the DB

        Attributes:
            db      (str):      File path to the db file
        """
        try:
            self.conn = sqlite3.connect(db)
            self.conn.cursor().execute("PRAGMA foreign_keys = 1")  #Enables foreign keys
        except IOError as e:
            print(e)

        self.initiate_db()

    def initiate_db(self):
        """
        Method used to create the database if it does not exist
        """
        sql_create_users_table = """ CREATE TABLE IF NOT EXISTS MembersTable (
                                        Tag text NOT NULL,
                                        Name text NOT NULL,
                                        TownHallLevel integer NOT NULL,
                                        League text,

                                        Discord_ID integer NOT NULL,
                                        Discord_JoinedDate date NOT NULL,

                                        in_PlanningServer text NOT NULL,
                                        is_Active text NOT NULL,
                                        Note text,
                                        PRIMARY KEY(Tag)
                                    ); """
        try:
            print("\n\n[-] Checking on MembersTable table.")                                    
            self.conn.cursor().execute(sql_create_users_table)
            self.conn.commit()
            print("[+] Active")

        except sqlite3.OperationalError as e:
            print(f"Failed to create with {e}")
            return e

        sql_create_update_table = """ CREATE TABLE IF NOT EXISTS DonationsTable (
                                        increment_date date NOT NULL,
                                        Tag text NOT NULL,
                                        Current_Donation integer NOT NULL,
                                        in_Zulu text NOT NULL,
                                        trophies integer NOT NULL,
                                        PRIMARY KEY (increment_date, Tag),
                                        CONSTRAINT coc_tag_constraint FOREIGN KEY (Tag) REFERENCES MembersTable(Tag)    
                                    ); """
        try:  
            print("\n[-] Checking on DonationsTable table")                                    
            self.conn.cursor().execute(sql_create_update_table)
            self.conn.commit()
            print("[+] Active")
            return None
        except sqlite3.OperationalError as e:
            print(f"OperationalError: {e}")
            return e


        

    def insert_userdata(self, tupe):
        """ 
        Populate the MembersTable table with user data, this is only done once.

        Parameters:
            tupe    (tuple):        Tuple of user

        Tuple:
            (Tag, Name, TownHallLevel, League, Discord_ID, Discord_JoinedDate, in_PlanningServer, is_Active, Note)
        """
        sql_update = """INSERT INTO MembersTable(
                    Tag,
                    Name,
                    TownHallLevel,
                    League,
                    Discord_ID,
                    Discord_JoinedDate,
                    in_PlanningServer,
                    is_Active,
                    Note) 
                    VALUES(?,?,?,?,?,?,?,?,?)
                        """  
        try:
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()
            return None

        except sqlite3.IntegrityError as e:
            print(e)
            return e

        except sqlite3.OperationalError as e:
            print(e)
            return e
        except Exception as e:
            print(e)
            return e
    
    def update_donations(self, tupe):
        """ 
        Update the donation table with new donation values

        Parameters:
            tupe    (tuple):        Tuple of user

        Tupe:
            (increment_date, Tag, current_donation, in_Zulu, trophies)
        """
        
        sql_update = """INSERT INTO DonationsTable(
                    increment_date,
                    Tag,
                    Current_Donation,
                    in_Zulu,
                    trophies)
                    VALUES(?,?,?,?,?)
                        """ 
        try:
            self.conn.cursor().execute(sql_update, tupe)
            self.conn.commit()
            return None

        except sqlite3.IntegrityError as e:
            print(e)
            print("Error with {}".format(tupe))
            return e
        except sqlite3.OperationalError as e:
            print(e)
            print("Error with this data {}".format(tupe))
            return e

    def is_Active(self, coc_tag):
        """ 
        Check to see if user has the is_Active flag set to true meaning that they
        are part of the clan still but just not present.

        Parameter:
            Tag   (str):      Tag of the user
        
        Returns:
            True or Flase + Note
        """
        sql_query = ("SELECT * FROM MembersTable WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (coc_tag,))
        self.conn.commit()
        row = cur.fetchall()

        if len(row) == 1:
            return row[0]
        else:
            msg = (f"Tag {coc_tag} was not found in MembersTable: in Function -->  is_Active()")
            print(msg)
            return msg

    def set_Active(self, tupe):
        """ 
        Change MembersTable active state to True or False. This will dictate if they are 
        currently enrolled into the clan.

        Parameter:
            tupe      (tuple):  

        Tuple:
            (str_bool, coc_tag)

            str_bool    (str): String boolean to change the value to
            coc_tag     (str): User CoC Tag
        """
        sql_query = ("UPDATE MembersTable SET is_Active = ? WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        #cur.execute(sql_query, (str_bool, coc_tag))
        self.conn.commit()

        sql_query = ("SELECT * FROM MembersTable WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (tupe[1],))
        #cur.execute(sql_query, (coc_tag,))
        row = cur.fetchall()
        
        if len(row) == 1:
            return tuple(row[0])
        else:
            print(f"MembersTable UPDATE failed: {tupe[1]} Not found: Function --> set_Active()")

    def set_kickNote(self, tupe):
        """ 
        Change users active state to True or False. This will dictate if they are 
        currently enrolled into the clan.

        Parameters:
            tupe        (tupe):

        Tuple:
            (msg, coc_tag)

            msg     (str):      Message about why the user is not part of the clan
            coc_tag (str):      CoC Clash tag
        """
        sql_query = ("UPDATE MembersTable SET Note = ?, is_Active = ? WHERE Discord_ID = ?")
        cur = self.conn.cursor()
        result = cur.execute(sql_query, tupe).rowcount
        #cur.execute(sql_query, (msg, coc_tag,))
        self.conn.commit()
        return result

    def set_inPlanning(self, tupe):
        """
        Method used to set the "in planning server" flag on

        Parameters:
            tupe        (tuple):

        Tuple:
            (str_bool, coc_tag)

            str_bool    (str):      String boolean to change the value to
            coc_tag     (str):      CoC Clash tag
        """
        sql_query = ("UPDATE MembersTable SET in_PlanningServer = ? WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        #cur.execute(sql_query, (str_bool, coc_tag,))
        self.conn.commit()

        sql_query = ("SELECT * FROM MembersTable WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, (tupe[1],))
        #cur.execute(sql_query, (coc_tag,))
        row = cur.fetchall()
        return row
        

    def update_users(self, tupe):
        """
        Method used to update a users. This is used when they level up or change clash league

        Parameters:
            tupe        (tuple):

        Tuple:
            (Tag, TownHallLevel, League)
        """
        sql_query = ("UPDATE MembersTable SET TownHallLevel = ?, League = ? WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        #cur.execute(sql_query, (TownHallLevel, League, Tag,))
        self.conn.commit()
        row = cur.fetchall()
        return row

    def get_allUsers(self):
        """ 
        Get all rows from MembersTable table
      
        Parementers:
            None
        """
        sql_query = ("SELECT * FROM MembersTable")
        cur = self.conn.cursor()
        cur.execute(sql_query)
        rows = cur.fetchall()
        return rows

    def get_allUsersWhereTrue(self):
        """ 
        Get all rows from MembersTable table
      
        Parementers:
            None
        """
        sql_query = ("SELECT * FROM MembersTable WHERE is_Active = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query , ('True',))
        rows = cur.fetchall()
        return rows

    def get_Donations(self, tupe):
        """ 
        Get all rows from DonationsTable table between last sunday and todays date

        Parameters:
            tupe        (tuple):

        Tuple:
            (coc_tag, sunday)

            coc_tag     (str):      Clash tag of the user
            sunday      (str):      Limiter to pull from
        """
        sql_query = ("SELECT * FROM DonationsTable WHERE Tag = ? AND increment_date BETWEEN ? AND ?")
        cur = self.conn.cursor()
        tupee = ((tupe[0], tupe[1], tupe[2]))
        cur.execute(sql_query, tupee)
        rows = cur.fetchall()
        return rows

    def get_user_byDiscID(self, tupe):
        """
        Returns the users clash tag by lookup up their discord ID

        Parameters:
            tupe        (tuple):

        Tuple:
            (disc_UserID)
            disc_UserID     (str):      Users discord ID
        """
        sql_query = ("SELECT * FROM MembersTable WHERE Discord_ID = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        rows = cur.fetchall()
        return rows
        
    def get_user_byTag(self, tupe):
        """
        Returns the users clash tag by lookup up their discord ID

        Parameters:
            tupe        (tuple):

        Tuple:
            (clash_tag)
            clash_tag     (str):      Users Clash ID
        """
        sql_query = ("SELECT * FROM MembersTable WHERE Tag = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        rows = cur.fetchall()
        return rows

    def get_user_byName(self, tupe):
        """
        Returns the users clash tag by lookup up their discord ID

        Parameters:
            tupe        (tuple):

        Tuple:
            (clash_name)
            clash_name     (str):      Users Clash ID
        """
        sql_query = ("SELECT * FROM MembersTable WHERE Name = ?")
        cur = self.conn.cursor()
        cur.execute(sql_query, tupe)
        rows = cur.fetchall()
        return rows
        


