import os
import sys
import copy
from gspread import Worksheet
from typing import List

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domains.dynamodb import BookingDynamoDB

from api.booking import TERAKOYA_TYPE, PLACE

from utils.mail import SesMail
from utils.spreadsheet import Spreadsheet
from utils.dt import DT

from config.google_config import TERAKOYA_SPREADSHEET_URL
from config.mail_config import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS

TERAKOYA_GMAIL_FROM = "" if TERAKOYA_GMAIL_ADDRESS is None else TERAKOYA_GMAIL_ADDRESS
TERAKOYA_GROUP_MAIL_CC = "" if TERAKOYA_GROUP_MAIL_ADDRESS is None else TERAKOYA_GROUP_MAIL_ADDRESS

MAIL_BODY_CONTACT = """
    <p>お会いできますことを心よりお待ちしております。</p>
    <p>塾長 前田</p>
    <br/>
    <p>このメールは送信専用メールアドレスから配信しています。</p>
    <p>返信頂いてもご回答できませんのでご了承ください。</p>
    <p>※予約キャンセルの場合やその他ご不明点等ありましたら、下記連絡先 または 公式LINE からご連絡下さい。</p>
    <p>＝＝＝＝＝＝＝連絡先＝＝＝＝＝＝＝＝</p>
    <p>電話番号：090-6543-0718</p>
    <p>メールアドレス：info@npoterakoya.org</p>
    <p>＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝</p>
"""

PLACE_DICT = {
    "サンシャインシティ": """
        <p>■サンシャインシティ住所</p>
        <p>〒170-8630</p>
        <p>東京都豊島区東池袋3丁目1</p>
        <p>ワールドインポートマートビル9階</p>
        <p>https://sunshinecity.jp/information/access_train.html</p>
        <p>16:50までに来れる場合は1Fのグローカルカフェ前集合でお願い致します。</p>
        <p>https://glocalcafe.jp/ikebukuro/</p>
        <p>16:50以降にお越しの場合は、添付画像の案内に従って直接お越し下さい。</p>
    """,
    "良品計画本社": """
        <p>■良品計画本社住所</p>
        <p>〒170-0013</p>
        <p>東京都豊島区</p>
        <p>東池袋4丁目26-3</p>
        <p>https://www.muji.com/jp/ja/shop/detail/046675</p>
        <p>初回参加の方や17:00以降に到着される場合はご案内致しますので公式LINEからご連絡下さい。</p>
        <p>よろしくお願いします。</p>
    """,
    "DIORAMA CAFE": """
        <p>■DIORAMA CAFE</p>
        <p>(池袋駅1b出口から徒歩1分) </p>
        <p>〒171-0021 </p>
        <p>東京都豊島区西池袋3-29-4 ジェスト7ビルB1</p>
        <p>https://tabelog.com/tokyo/A1305/A130501/13234609/</p>
    """,
    "キカガク": """
        <p>■株式会社キカガク住所</p>
        <p>〒150-0041</p>
        <p>東京都渋谷区神南 1-9-2</p>
        <p>大畠ビル202号室</p>
        <p>https://www.kikagaku.co.jp/mission/</p>
    """,
    "キャリア・マム": """
        <p>■おしごとカフェ キャリア・マム住所</p>
        <p>〒206-0033</p>
        <p>東京都多摩市落合1-46-1 ココリア多摩センター5階</p>
        <p>http://www.c-mam.co.jp/oshigoto_cafe/</p>
    """
}


class Remind():
    __ses_client = SesMail(TERAKOYA_GMAIL_FROM)

    # booking_date, terakoya_type are used only for spreadsheet
    def __init__(self, name: str, place: str, email: str, booking_date: str = "", terakoya_type: str = "") -> None:
        self.name = name
        self.place = place
        self.email = email
        self.booking_date = booking_date
        self.terakoya_type = terakoya_type

    def send_remind_mail(self):
        subject = '【カフェ塾テラコヤ】ご参加当日のお知らせ'
        body = f"""
            <p>{self.name}様</p>
            <p>カフェ塾テラコヤへの参加予約ありがとうございました。</p>
            <p>ご予約の当日となりましたので、お知らせ申し上げます。</p>
            <p>本日は、{self.place}にお越し下さい。</p>
            <p>住所の詳細等につきましては本メール下部に記載しておりますので、ご確認下さい。</p>
            <br/>
            {MAIL_BODY_CONTACT}
            <br/>
            {PLACE_DICT[self.place]}
        """
        img_fpath = os.path.join(ROOT_DIR_PATH, "assets", "sunshine-map.jpg") if self.place == "サンシャインシティ" else ""
        self.__ses_client.send(self.email, subject, body, TERAKOYA_GROUP_MAIL_CC, img_fpath)


SYSTEM_SHEET_COLUMN_ALPHABET_DICT = {
    "名前": "A",
    "メールアドレス": "B",
    "参加日": "C",
    "参加希望": "D",
    "拠点": "E",
    "リマインドメール送信済み": "F"
}


# TODO: Delete　this after the way using DynamoDB starts
class RemindSpreadsheet(Remind):
    def update_is_reminded(self, worksheet: Worksheet):
        match_row_numbers = self.__find_match_row_numbers(worksheet)
        cell_address = SYSTEM_SHEET_COLUMN_ALPHABET_DICT["リマインドメール送信済み"] + str(match_row_numbers[0])  # ex: B5
        worksheet.update_acell(cell_address, "済")

    def __find_match_row_numbers(self, worksheet: Worksheet) -> List[int]:
        search_keywords = [self.email, self.booking_date,
                           self.terakoya_type, self.place]
        match_row_numbers: List[int] = []
        for search_word in search_keywords:
            cells = worksheet.findall(search_word)
            # get a list of the cell's row numbers
            row_numbers: List[int] = [cell.row for cell in cells]
            if len(match_row_numbers) == 0:
                match_row_numbers = row_numbers
            else:
                # get a intersection of row numbers common to two lists
                match_row_numbers = list(set(
                    copy.copy(match_row_numbers)) & set(row_numbers))
        return match_row_numbers

    def should_send_email(self):
        """
        whether date diff is within a day (24h)
        return -2 < diff_days < 2 : whether it's from 2 days before to 2 days after
        """
        return (DT.convert_slashdate_to_datetime(self.booking_date) - DT.CURRENT_JST_DATETIME).days == 0


def main_spreadsheet(sheet_name: str = "system"):
    """
    NOTE: possible to spcity another sheet_name for test
    """
    system_sheet = Spreadsheet(TERAKOYA_SPREADSHEET_URL).get_worksheet(sheet_name)
    records_after_today = [rec for rec in system_sheet.get_all_records() if DT.convert_slashdate_to_datetime(
        rec["参加日"]) > DT.CURRENT_JST_DATETIME and rec["リマインドメール送信済み"] != "済"]
    for record in records_after_today:
        print(f"Record: {str(dict(record))}")
        try:
            remind_spreadsheet = RemindSpreadsheet(
                record["名前"], record["拠点"], record["メールアドレス"], record["参加日"], record["参加希望"])
            if (not (remind_spreadsheet.should_send_email())):
                print("No need to send a email")
                continue
            if (remind_spreadsheet.terakoya_type == "カフェ塾テラコヤ(池袋)" and remind_spreadsheet.place == ""):
                print("Impossible to send a email because of no place filled in Ikebukuro")
                continue
            remind_spreadsheet.send_remind_mail()
            remind_spreadsheet.update_is_reminded(system_sheet)
        except:
            continue


def main_dynamodb():
    # Map定義
    # https://terakoya20220112.slack.com/archives/C02V0PHDGP2/p1675009220056179
    PLACE_MAP = {
        0: "",  # 未設定状態
        1: "サンシャインシティ",
        2: "良品計画本社",
        3: "DIORAMA CAFE",
        4: "キャリア・マム",
        5: "キカガク"
    }

    bk_item_list = BookingDynamoDB.get_item_list_for_remind()
    for bk_item in bk_item_list:
        print(f"Booking Item: {str(bk_item.__dict__)}")
        try:
            if (bk_item.terakoya_type == TERAKOYA_TYPE.HIGH_IKE and bk_item.place == PLACE.TBD):
                print("Impossible to send a email because of no place filled in Ikebukuro")
                continue
            Remind(bk_item.name, PLACE_MAP[bk_item.place], bk_item.email).send_remind_mail()
            BookingDynamoDB.update_is_reminded(bk_item.sk)
        except Exception as e:
            print(f"Error happend. Error message: {str(e)}")


def lambda_handler(event, context):
    try:
        # main_spreadsheet()
        main_dynamodb()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")


if __name__ == '__main__':
    # main_spreadsheet("system_test")
    main_dynamodb()
    pass
