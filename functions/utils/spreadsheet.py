import os
import sys
import gspread
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

GCP_KEY_FPATH = os.path.join(ROOT_DIR_PATH, "config", "_gcp_service_account_key.json")
SCOPE = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]


class Spreadsheet():
    __client = gspread.authorize(
        ServiceAccountCredentials.from_json_keyfile_name(GCP_KEY_FPATH))

    def __init__(self, url) -> None:
        self.spread_sheet = self.__client.open_by_url(url)

    def get_worksheet(self, sheet_name) -> Worksheet:
        return self.spread_sheet.worksheet(sheet_name)
