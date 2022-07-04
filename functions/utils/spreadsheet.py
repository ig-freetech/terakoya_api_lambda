import os
import sys
import copy
import gspread
from gspread.worksheet import Worksheet
from oauth2client.service_account import ServiceAccountCredentials
from typing import List, Dict, Literal, Union
from utils.dt import CURRENT_DATETIME, convert_to_datetime

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

KEY_FILE_NAME = "gcp_service_account_key_terakoya-dev.json"
KEY_FILE_PATH = os.path.join(ROOT_DIR_PATH, "config", KEY_FILE_NAME)
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_PATH)
client = gspread.authorize(credentials)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFjUeVX36bSsGVoyRtFO1CJX8uVc52wAx6O2pvSbdUk/edit#gid=306935450"
spread_sheet = client.open_by_url(SHEET_URL)

SYSTEM_SHEET = "system"
MAIN_SHEET = "参加予約_system"

system_sheet = spread_sheet.worksheet(SYSTEM_SHEET)
main_sheet = spread_sheet.worksheet(MAIN_SHEET)

COLUMN_INDEX_DICT: Dict[str, str] = {
    "名前": "A",
    "メールアドレス": "B",
    "参加日": "C",
    "参加希望": "D",
    "拠点": "E",
    "リマインドメール送信済み": "F"
}
SYSTEM_COLUMN_NAME_TYPES = Literal["名前", "メールアドレス",
                                   "参加日", "参加希望", "拠点", "リマインドメール送信済み"]
MAIN_COLUMN_NAME_TYPES = Literal["タイムスタンプ", "名前", "参加希望", "何時頃来れそうですか？（活動時間17時〜20時）", "学年",
                                 "参加希望日", "テラコヤへのご参加は？", "勉強したい科目", "その科目の内容をできるだけ詳しく教えてください",
                                 "希望する勉強の仕方", "今在籍している学校", "文理選択", "将来の夢、志望大学（自由記述）", "好きなもの、こと",
                                 "テラコヤを知ったキッカケ", "メールアドレス(予約確認メールを送らせて頂きます※機能調整中です）", "備考"]

SHEET_DICT: Dict[str, Worksheet] = {
    "system": system_sheet,
    "main": main_sheet
}
SHEET_TYPES = Literal["system", "main"]


def append_row_to_sheet(sheet_type: SHEET_TYPES, row: List[str]):
    SHEET_DICT[sheet_type].append_row(row)


def get_system_future_records() -> List[dict[SYSTEM_COLUMN_NAME_TYPES, str]]:
    all_records = system_sheet.get_all_records()
    filterd_records = [rec for rec in all_records if convert_to_datetime(
        rec["参加日"]) > CURRENT_DATETIME]
    return filterd_records


def get_main_future_records() -> List[dict[Union[Literal["参加希望日", "メールアドレス", "参加希望"], str], str]]:
    all_records = main_sheet.get_all_records()
    filterd_records = [rec for rec in all_records if len(
        [x for x in rec["参加希望日"].split(",") if convert_to_datetime(x) > CURRENT_DATETIME]) > 0]
    return filterd_records


def find_cell_address(search_words: List[str], column_name: SYSTEM_COLUMN_NAME_TYPES) -> str:
    candidate_row_numbers: List[int] = []
    for search_word in search_words:
        cells = system_sheet.findall(search_word)
        row_numbers = [cell.row for cell in cells]
        if len(candidate_row_numbers) == 0:
            candidate_row_numbers = row_numbers
        else:
            candidate_row_numbers = list(set(
                copy.deepcopy(candidate_row_numbers)) & set(row_numbers))
    return COLUMN_INDEX_DICT[column_name] + str(candidate_row_numbers[0])


def update_cell(cell_address: str, value: str):
    system_sheet.update_acell(cell_address, value)


def test():
    search_words = ["i.g.freetech2021@gmail.com",
                    "7/2 (土)", "テラコヤ中等部(渋谷)", "キカガク"]
    cell_addr = find_cell_address(search_words, "リマインドメール送信済み")
    update_cell(cell_address=cell_addr, value="済")


if __name__ == "__main__":
    test()
