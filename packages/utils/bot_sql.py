from typing import List

from packages.database_schema import *


def sql_create_tables() -> List[str]:
    return [
        create_discord_users(),
        create_clash_account(),
        create_user_note(),
        create_clash_update(),
        create_clash_classic_update(),
        create_clash_classic_view()
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


def sql_update_discord_user_set_active() -> str:
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


def sql_select_clash_account_discord_id() -> str:
    return '''SELECT * FROM clash_account WHERE discord_id = $1'''


def sql_update_clash_account_coc_alt_cascade() -> str:
    return '''UPDATE clash_account SET is_primary_account = $1 WHERE discord_id = $2'''


def sql_update_clash_account_coc_alt_primary() -> str:
    return '''UPDATE clash_account SET is_primary_account = $1 WHERE discord_id = $2 AND clash_tag = $3'''


def sql_delete_clash_account_record() -> str:
    return '''DELETE FROM clash_account WHERE clash_tag = $1 AND discord_id = $2'''


#
# Manipulate user_note
#
def sql_insert_user_note() -> str:
    return '''INSERT INTO user_note(discord_id, clash_tag, note_date, commit_by, note) VALUES($1, $2, $3, $4, $5)'''


#
# Donation queries
#

def sql_select_user_donation() -> str:
    return "SELECT * FROM clash_classic_update_view WHERE week_date='{}' AND clash_tag='{}'"


def sql_select_active_account() -> str:
    return '''SELECT * FROM discord_user, clash_account 
    WHERE discord_user.discord_id = clash_account.discord_id
    AND discord_user.is_active = 'true'
    AND clash_account.is_primary_account = 'true' 
    AND discord_user.discord_id = '{}';'''


#
# Group stat queries
#
def sql_select_all_active_users() -> str:
    return '''SELECT * FROM discord_user, clash_account, clash_classic_update_view
    WHERE discord_user.discord_id = clash_account.discord_id
    AND discord_user.is_active = 'true'
    AND clash_account.is_primary_account = 'true' 
    AND clash_account.clash_tag = clash_classic_update_view.clash_tag
    AND clash_classic_update_view.week_date = '{}'
    '''


def sql_select_clash_members_not_registered() -> str:
    return '''
    SELECT * FROM present_in_clan
    WHERE present_in_clan.clash_tag NOT IN (
        SELECT clash_tag FROM discord_user, clash_account
        WHERE discord_user.discord_id = clash_account.discord_id
        AND discord_user.is_active = 'true'
        AND clash_account.is_primary_account = 'true'
        );
    '''


def sql_select_classic_view() -> str:
    return '''\
    SELECT * FROM
    clash_classic_update_view as cw, clash_account, discord_user
    WHERE cw.clash_tag IN (
        SELECT 
            clash_tag
        FROM 
            discord_user, clash_account
        WHERE
            discord_user.discord_id = clash_account.discord_id
        AND
            discord_user.is_active = 'true'
        AND
            clash_account.is_primary_account = 'true'
    )
    AND cw.clash_tag = clash_account.clash_tag
    AND clash_account.discord_id = discord_user.discord_id
    AND week_date = '{}';
    '''


#
# Get a user from the databas
#
def sql_select_member_find() -> str:
    """
    Find a user in the database by searching nickname, name, discriminator, clash tag etc
    $1: Any string casted to upper
    $2: Integer
    Returns
    -------

    """
    return '''\
SELECT * FROM discord_user, clash_account
WHERE
    (
        UPPER(discord_nickname) = $1
        OR UPPER(discord_name) = $1
        OR discord_user.discord_id = $2
        OR CONCAT(UPPER(discord_name),'#', discord_discriminator) = $1
        OR UPPER(clash_account.clash_tag) = $1
        OR UPPER(TRIM(LEADING '#' FROM clash_account.clash_tag)) = $1
    )
    AND discord_user.discord_id = clash_account.discord_id;
    '''
