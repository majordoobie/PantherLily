from typing import List

from packages.database_schema import *

def sql_create_tables() -> List[str]:
    return [
        create_discord_users(),
        create_clash_account(),
        create_user_note(),
        create_clash_update()
    ]

#
# Manipulate discord_user
#
def sql_select_discord_user_id() -> str:
    return 'SELECT * FROM discord_user WHERE discord_id = $1'

def sql_insert_discord_user() -> str:
    return '''INSERT INTO discord_user(
                    discord_id, discord_name, discord_nickname, discord_discriminator, 
                    guild_join_date, global_join_date, db_join_date, in_zulu_base_planning, 
                    in_zulu_server, is_active) 
                    VALUES (
                    $1, $2, $3, $4, $5, $6, $7, false, true, true)'''

def sql_update_discord_user_is_active() -> str:
    return '''UPDATE discord_user SET is_active = $1 WHERE discord_id = $2'''

#
# Manipulate clash_account
#
def sql_insert_clash_account() -> str:
    return '''INSERT INTO clash_account(
                    clash_tag, discord_id, is_primary_account) VALUES (
                    $1, $2, true)'''

def sql_select_clash_account_tag() -> str:
    return '''SELECT * FROM clash_account WHERE clash_tag = $1'''

def sql_select_clash_account_discordid() -> str:
    return '''SELECT * FROM clash_account WHERE discord_id = $1'''

def sql_update_clash_account_coc_alt_all_false() -> str:
    return '''UPDATE clash_account SET is_primary_account = $1 WHERE discord_id = $2'''

def sql_update_clash_account_coc_alt_primary() -> str:
    return '''UPDATE clash_account SET is_primary_account = $1 WHERE discord_id = $2 AND clash_tag = $3'''

def sql_delete_clash_account_record() -> str:
    return '''DELETE FROM clash_account WHERE clash_tag = $1 AND discord_id = $2'''