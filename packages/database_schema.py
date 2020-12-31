"""
 File should only be used once and it is placed in the Docker-compose
 of the database in order to stand it up.
"""
from typing import List


def drop_tables() -> List[str]:
    sqls = [
        "DROP TABLE discord_user CASCADE ;",
        "DROP TABLE clash_account CASCADE;",
        "DROP TABLE clash_update CASCADE;",
        "DROP TABLE user_note CASCADE;"
    ]

def create_discord_users() -> str:
    sql = ('''\
CREATE TABLE IF NOT EXISTS discord_user (
    discord_id BIGINT PRIMARY KEY,
    discord_name TEXT NOT NULL,
    discord_nickname TEXT,
    discord_discriminator TEXT,

    guild_join_date TIMESTAMP NOT NULL,
    global_join_date TIMESTAMP,
    db_join_date TIMESTAMP,

    in_zulu_base_planning BOOLEAN DEFAULT false,
    in_zulu_server BOOLEAN DEFAULT false,
    is_active BOOLEAN NOT NULL
);
''')
    return sql

def create_clash_account() -> str:
    sql = ('''\
CREATE TABLE IF NOT EXISTS clash_account (
    clash_tag TEXT PRIMARY KEY,
    discord_id BIGINT NOT NULL,
    is_primary_account BOOLEAN NOT NULL DEFAULT true,
    FOREIGN KEY (discord_id) REFERENCES discord_user (discord_id)
    ON DELETE CASCADE
);
''')
    return sql


def create_user_note() -> str:
    sql = ('''\
CREATE TABLE IF NOT EXISTS user_note (
    note_id SERIAL NOT NULL PRIMARY KEY,
    discord_id BIGINT NOT NULL,
    clash_tag TEXT NOT NULL,
    note_date timestamp NOT NULL,
    commit_by BIGINT NOT NULL,
    note TEXT NOT NULL,
    FOREIGN KEY (discord_id) REFERENCES discord_user (discord_id) ON DELETE CASCADE,
    FOREIGN KEY (clash_tag) REFERENCES clash_account (clash_tag), 
    FOREIGN KEY (commit_by) REFERENCES discord_user (discord_id)
);
''')
    return sql

def create_clash_classic_update() -> str:
    sql = ('''\
CREATE TABLE IF NOT EXISTS clash_classic_update (
    increment_date TIMESTAMP NOT NULL,
    tag TEXT NOT NULL,
    current_donations INTEGER NOT NULL,
    current_clan TEXT,
    PRIMARY KEY (increment_date, tag),
    FOREIGN KEY (tag) REFERENCES clash_account (clash_tag) ON DELETE CASCADE
);    
    ''')
    return sql


def create_clash_update() -> str:
    sql = ('''\
CREATE TABLE IF NOT EXISTS clash_update (
    record_id BIGSERIAL PRIMARY KEY,
    update_time TIMESTAMP NOT NULL,

    -- Clash
    clash_tag TEXT NOT NULL,
    clash_name TEXT NOT NULL,
    clash_share_link TEXT NOT NULL,
    clash_badge_name TEXT NOT NULL,
    clash_badge_url TEXT NOT NULL,
    clash_role TEXT,
    clash_clan_tag TEXT NOT NULL,
    clash_clan_name TEXT NOT NULL,
    clash_town_hall INTEGER DEFAULT 0,
    clash_attack_wins INTEGER,
    clash_defense_wins INTEGER,
    clash_trophies INTEGER,
    clash_best_trophies INTEGER,
    clash_war_stars INTEGER,
    clash_donations INTEGER,

    -- ACC
    ACC_bigger_coffers INTEGER DEFAULT 0,
    ACC_get_those_goblins INTEGER DEFAULT 0,
    ACC_bigger_and_better INTEGER DEFAULT 0,
    ACC_nice_and_tidy INTEGER DEFAULT 0,
    ACC_release_the_beasts INTEGER DEFAULT 0,
    ACC_gold_grab INTEGER DEFAULT 0,
    ACC_elixir_escapade INTEGER DEFAULT 0,
    ACC_sweet_victory INTEGER DEFAULT 0,
    ACC_empire_builder INTEGER DEFAULT 0,
    ACC_wall_buster INTEGER DEFAULT 0,
    ACC_humiliator INTEGER DEFAULT 0,
    ACC_union_buster INTEGER DEFAULT 0,
    ACC_conqueror INTEGER DEFAULT 0,
    ACC_unbreakable INTEGER DEFAULT 0,
    ACC_friend_in_need INTEGER DEFAULT 0,
    ACC_mortar_mauler INTEGER DEFAULT 0,
    ACC_heroic_heist INTEGER DEFAULT 0,
    ACC_league_allstar INTEGER DEFAULT 0,
    ACC_xbow_exterminator INTEGER DEFAULT 0,
    ACC_firefighter INTEGER DEFAULT 0,
    ACC_war_hero INTEGER DEFAULT 0,
    ACC_treasurer INTEGER DEFAULT 0,
    ACC_antiartillery INTEGER DEFAULT 0,
    ACC_sharing_is_caring INTEGER DEFAULT 0,
    ACC_keep_your_village_safe INTEGER DEFAULT 0,
    ACC_master_engineering INTEGER DEFAULT 0,
    ACC_next_generation_model INTEGER DEFAULT 0,
    ACC_unbuild_it INTEGER DEFAULT 0,
    ACC_champion_builder INTEGER DEFAULT 0,
    ACC_high_gear INTEGER DEFAULT 0,
    ACC_hidden_treasures INTEGER DEFAULT 0,
    ACC_games_champion INTEGER DEFAULT 0,
    ACC_dragon_slayer INTEGER DEFAULT 0,
    ACC_war_league_legend INTEGER DEFAULT 0,


    -- TROOP
    TROOP_archer INTEGER DEFAULT 0,
    TROOP_barbarian INTEGER DEFAULT 0,
    TROOP_baby_dragon INTEGER DEFAULT 0,
    TROOP_balloon INTEGER DEFAULT 0,
    TROOP_bowler INTEGER DEFAULT 0,
    TROOP_dragon INTEGER DEFAULT 0,
    TROOP_electro_dragon INTEGER DEFAULT 0,
    TROOP_giant INTEGER DEFAULT 0,
    TROOP_goblin INTEGER DEFAULT 0,
    TROOP_golem INTEGER DEFAULT 0,
    TROOP_healer INTEGER DEFAULT 0,
    TROOP_hog_rider INTEGER DEFAULT 0,
    TROOP_ice_golem INTEGER DEFAULT 0,
    TROOP_lava_hound INTEGER DEFAULT 0,
    TROOP_miner INTEGER DEFAULT 0,
    TROOP_minion INTEGER DEFAULT 0,
    TROOP_pekka INTEGER DEFAULT 0,
    TROOP_yeti INTEGER DEFAULT 0,
    TROOP_valkyrie INTEGER DEFAULT 0,
    TROOP_witch INTEGER DEFAULT 0,
    TROOP_wall_breaker INTEGER DEFAULT 0,
    TROOP_wizard INTEGER DEFAULT 0,

    TROOP_wall_wrecker INTEGER DEFAULT 0,
    TROOP_stone_slammer INTEGER DEFAULT 0,
    TROOP_siege_barracks INTEGER DEFAULT 0,
    TROOP_battle_blimp INTEGER DEFAULT 0,

    -- SPELLS
    SPELL_lightning_spell INTEGER DEFAULT 0,
    SPELL_healing_spell INTEGER DEFAULT 0,
    SPELL_rage_spell INTEGER DEFAULT 0,
    SPELL_jump_spell INTEGER DEFAULT 0,
    SPELL_freeze_spell INTEGER DEFAULT 0,
    SPELL_clone_spell INTEGER DEFAULT 0,
    SPELL_poison_spell INTEGER DEFAULT 0,
    SPELL_earthquake_spell INTEGER DEFAULT 0,
    SPELL_haste_spell INTEGER DEFAULT 0,
    SPELL_skeleton_spell INTEGER DEFAULT 0,
    SPELL_bat_spell INTEGER DEFAULT 0,

    -- HEROES
    HERO_barbarian_king INTEGER DEFAULT 0,
    HERO_archer_queen INTEGER DEFAULT 0,
    HERO_grand_warden INTEGER DEFAULT 0,
    HERO_royal_champion INTEGER DEFAULT 0,
    HERO_battle_machine INTEGER DEFAULT 0,

    -- SIEGE
    SIEGE_wall_wrecker INTEGER DEFAULT 0,
    SIEGE_battle_blimp INTEGER DEFAULT 0,
    SIEGE_stone_slammer INTEGER DEFAULT 0,
    SIEGE_siege_barracks INTEGER DEFAULT 0,

    FOREIGN KEY (clash_tag) REFERENCES clash_account (clash_tag)
    ON DELETE CASCADE 
);
''')
    return sql