import discord
from datetime import datetime, timedelta
import coc

async def update_donationstable(dbcon, coc_api):
    """Function used to retrive all active players to feed to commit_database

     Keyword arguments:
     ctx -- Discord context
     db -- Database handle
     coc_api -- coc.py client

     Return:
     No returns"""
    active_members = [tag[0] for tag in dbcon.get_all_active()]
    async for player in coc_api.get_players(active_members):
        commit_database(player, dbcon)

async def update_user(dbcon, coc_api, user_tag):
    """Function used to retrive a single player to feed to commit_database

     Keyword arguments:
     ctx -- Discord context
     db -- Database handle
     coc_api -- coc.py client
     user_tag -- Tag of member you want to update

     Return:
     No returns"""  
    player = await coc_api.get_player(user_tag)
    commit_database(player, dbcon)

def commit_database(player, dbcon):
    """Function used to update donations table with upto date data using coc.py

     Keyword arguments:
     player -- coc.py SearchPlayer object
     dbcon -- Database handle

     Return:
     No returns"""
    in_zulu = "False"
    try:
        if player.clan.name == "Reddit Zulu":
            in_zulu = "True"
    except:
        in_zulu = "False"

    # Commit to database 
    dbcon.update_donations((
        datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'),
        player.tag,
        player.achievements_dict["Friend in Need"].value,
        in_zulu,
        player.trophies
    ))
