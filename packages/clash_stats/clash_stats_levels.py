from pathlib import Path
import pandas as pd

from oauth2client.service_account import ServiceAccountCredentials
import gspread


class ClashTroopLevel:
    ROOT_PATH = Path(".").resolve() / "packages/private/PantherLily_Keys/google_login.json"

    def __init__(self, payload: dict):
        self.name = payload['name']
        self.town_hall = payload['town_hall']
        self.max_level = payload['max_level']
        self.type = payload['type']
        self.source = payload['source']
        self.emoji = payload['emoji']

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self.__dict__)


def download_sheets() -> None:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    json_path = ClashTroopLevel.ROOT_PATH
    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)
    client = gspread.authorize(creds)
    workbook = client.open('Clash of Clans Troop Levels')
    sheet = workbook.get_worksheet(0)
    troop_df = pd.DataFrame(sheet.get_all_records())
    troop_df.to_csv(Path(".").resolve() / "assets/CoC_Troop_Levels2.csv", index=False)


def get_troop_df() -> pd.DataFrame:
    troop_df = pd.read_csv(
        Path(".").resolve() / "assets/CoC_Troop_Levels2.csv",
        skip_blank_lines=True,
        header=0,
        dtype={"max_level": "Int32"}
    ).set_index('Object', drop=False)
    return troop_df


def get_df_level(troop_df: pd.DataFrame, level: int) -> dict:
    town_hall = f'TH{level}'
    troop_df = troop_df.loc[troop_df[town_hall] > 0, ['Object', 'Type', 'Source', 'Emoji', town_hall]]
    troop_df[town_hall] = troop_df[town_hall].astype(int)
    troop_df['town_hall'] = level
    troop_df = troop_df.transpose().rename(
        {'Object': 'name',
         'Type': 'type',
         'Source': 'source',
         town_hall: 'max_level',
         'Emoji': 'emoji'})
    return troop_df


def get_df_and_level(level: int) -> dict:
    town_hall = f'TH{level}'
    troop_df = pd.read_csv(
        Path(".").resolve() / "assets/CoC_Troop_Levels2.csv",
        skip_blank_lines=True,
        header=0,
        dtype={"max_level": "Int32"}
    ).set_index('Object', drop=False)

    troop_df = troop_df.loc[troop_df[town_hall] > 0, ['Object', 'Type', 'Source', 'Emoji', town_hall]]
    troop_df[town_hall] = troop_df[town_hall].astype(int)
    troop_df['town_hall'] = level
    troop_df = troop_df.transpose().rename(
        {'Object': 'name',
         'Type': 'type',
         'Source': 'source',
         town_hall: 'max_level',
         'Emoji': 'emoji'})

    return troop_df
