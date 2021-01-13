from sys import argv

from oauth2client.service_account import ServiceAccountCredentials
import gspread

class ClashTroopLevel:
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


def _get_spreadsheet() -> list:
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('/opt/project/packages/private/google_login.json', scope)
    client = gspread.authorize(creds)
    workbook = client.open('Clash of Clans Troop Levels')
    sheet = workbook.get_worksheet(0)
    return sheet.get_all_records()


def get_levels(level: int) -> dict:
    clash_data = _get_spreadsheet()
    town_hall = 'TH' + str(level)
    results_obj = {}

    for troop in clash_data:
        if troop[town_hall]:
            if isinstance(troop['Object'], str):
                results_obj[troop['Object']] = ClashTroopLevel({
                    'name': troop['Object'],
                    'town_hall': town_hall,
                    'max_level': troop[town_hall],
                    'type': troop['Type'],
                    'source': troop['Source'],
                    'emoji': troop['Emoji'],
                })

    return results_obj


if __name__ == '__main__':
    if argv[1].isdigit():
        get_levels(int(argv[1]))
    else:
        print("Provide an integer for the town hall level")
