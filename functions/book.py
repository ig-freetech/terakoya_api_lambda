import os
import sys
import json
from abc import ABCMeta, abstractmethod

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domains.dynamodb import BookingDynamoDB, BookingItem

from utils.mail import SesMail
from utils.dt import DT
from utils.spreadsheet import Spreadsheet

from config.mail_config import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS
from config.google_config import TERAKOYA_SPREADSHEET_URL

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


MAIN_SHEET_TIMESTAMP_FORMAT = f"%Y/%m/%d %H:%M:%S"


class IBooking(metaclass=ABCMeta):
    ses_client = SesMail(TERAKOYA_GMAIL_FROM)

    def __init__(self, event_body) -> None:
        request_body = json.loads(event_body)
        self.name = request_body["name"]
        self.email = request_body["email"]
        self.terakoya_type = request_body["terakoya_type"]
        self.attendance_date_list = request_body["attendance_date_list"]
        self.arrival_time = request_body["arrival_time"]
        self.grade = request_body["grade"]
        self.terakoya_experience = request_body["terakoya_experience"]
        self.study_subject = request_body["study_subject"]
        self.study_subject_detail = request_body["study_subject_detail"]
        self.study_style = request_body["study_style"]
        self.school_name = request_body["school_name"]
        self.course_choice = request_body["course_choice"]
        self.future_free = request_body["future_free"]
        self.like_thing_free = request_body["like_thing_free"]
        self.how_to_know_terakoya = request_body["how_to_know_terakoya"]
        self.remarks = request_body["remarks"]

    @abstractmethod
    def send_confirmation_email(self) -> None:
        raise NotImplementedError()

    @abstractmethod
    def book(self) -> None:
        raise NotImplementedError()


# TODO: Delete this after the way using DynamoDB starts
class BookingViaSpreadsheet(IBooking):
    """
    NOTE: change main and system's sheet name to another one to test
    """
    __spread_sheet = Spreadsheet(TERAKOYA_SPREADSHEET_URL)
    # for test
    __main_sheet = __spread_sheet.get_worksheet("main_test")
    __system_sheet = __spread_sheet.get_worksheet("system_test")
    # __main_sheet = __spread_sheet.get_worksheet("参加予約_system")
    # __system_sheet = __spread_sheet.get_worksheet("system")

    TERAKOYA_TYPE_PLACE_DICT = {
        "カフェ塾テラコヤ(池袋)": "",
        "オンラインテラコヤ(多摩)": "キャリア・マム",
        "テラコヤ中等部(池袋)": "サンシャインシティ",
        "テラコヤ中等部(渋谷)": "キカガク"
    }

    def __record_to_main(self):
        dt_jst = DT.CURRENT_JST_DATETIME.strftime(MAIN_SHEET_TIMESTAMP_FORMAT)
        print(f"Record: {self.email},{self.attendance_date_list},{self.terakoya_type}")
        if (self.__exists_record_in_main()):
            print("Already registered in Main")
            return
        self.__main_sheet.append_row([
            dt_jst,
            self.name,
            self.terakoya_type,
            self.arrival_time,
            self.grade,
            ",".join(self.attendance_date_list),
            self.terakoya_experience,
            self.study_subject,
            self.study_subject_detail,
            self.study_style,
            self.school_name,
            self.course_choice,
            self.future_free,
            self.like_thing_free,
            self.how_to_know_terakoya,
            self.email,
            self.remarks
        ])

    def __record_to_system(self):
        for attendance_date in self.attendance_date_list:
            print(f"Record: {self.email},{attendance_date},{self.terakoya_type}")
            if (self.__exists_record_in_system(attendance_date)):
                print("Already registered in System")
                continue
            self.__system_sheet.append_row([
                self.name,
                self.email,
                attendance_date,
                self.terakoya_type,
                self.TERAKOYA_TYPE_PLACE_DICT[self.terakoya_type]
            ])

    def __exists_record_in_main(self):
        records_after_today = [rec for rec in self.__main_sheet.get_all_records() if len(
            [x for x in rec["参加希望日"].split(",") if DT.convert_slashdate_to_datetime(x) > DT.CURRENT_JST_DATETIME]) > 0]
        same_records = [rec for rec in records_after_today
                        if len(list(set(rec["参加希望日"].split(",")) ^ set(self.attendance_date_list))) == 0
                        and rec["メールアドレス"] == self.email
                        and rec["参加希望"] == self.terakoya_type
                        ]
        return len(same_records) > 0

    def __exists_record_in_system(self, attendance_date: str):
        records_after_today = [rec for rec in self.__system_sheet.get_all_records() if DT.convert_slashdate_to_datetime(
            rec["参加日"]) > DT.CURRENT_JST_DATETIME]
        searched_records = [rec for rec in records_after_today
                            if rec["参加日"] == attendance_date
                            and rec["メールアドレス"] == self.email
                            and rec["参加希望"] == self.terakoya_type
                            ]
        return len(searched_records) > 0

    def send_confirmation_email(self) -> None:
        subject = "【カフェ塾テラコヤ】参加予約完了"
        body = f"""
            <p>{self.name}様</p>
            <p>カフェ塾テラコヤへの参加予約が完了致しました。</p>
            <p>予約内容は以下の通りです。</p>
            <br/>
            <p>参加区分: {self.terakoya_type}</p>
            <p>参加希望日: {",".join(self.attendance_date_list)}</p>
            <p>来れそうな時間帯: {self.arrival_time}</p>
            <p>テラコヤへの参加経験: {self.terakoya_experience}</p>
            <p>備考: {self.remarks}</p>
            <br/>
            {MAIL_BODY_CONTACT}
        """
        self.ses_client.send(self.email, subject, body, TERAKOYA_GROUP_MAIL_CC)

    def book(self) -> None:
        print(f"Record: {str(self.__dict__)}")
        self.__record_to_main()
        self.__record_to_system()
        self.send_confirmation_email()
        print("Record completed!")


class BookingViaDynamoDB(IBooking):
    # Map定義
    # https://terakoya20220112.slack.com/archives/C02V0PHDGP2/p1675009220056179
    TERAKOYA_TYPE_MAP = {
        1: 'カフェ塾テラコヤ(池袋)',
        2: 'オンラインテラコヤ(多摩)',
        3: 'テラコヤ中等部(池袋)',
        4: 'テラコヤ中等部(渋谷)',
        0: 'その他'
    }
    ARRIVAL_TIME_MAP = {
        1: '17:00前',
        2: '17:00~17:30',
        3: '17:30~18:00',
        4: '18:00以降',
        0: 'その他'
    }
    TERAKOYA_EXPERIENCE_MAP = {
        1: '今回が初回',
        2: '過去に参加したことがある',
        0: 'その他'
    }
    TERAKOYA_TYPE_TO_PLACE_MAP = {
        0: 0,  # その他 -> TBD
        1: 0,  # カフェ塾テラコヤ(池袋) -> TBD
        2: 4,  # オンラインテラコヤ(多摩) -> キャリア・マム
        3: 1,  # テラコヤ中等部(池袋) -> サンシャインシティ
        4: 5,  # テラコヤ中等部(渋谷) -> キカガク
    }

    def __init__(self, event_body) -> None:
        super().__init__(event_body)
        self.booking_item_list = [BookingItem(
            date,
            self.email,
            self.terakoya_type,
            self.TERAKOYA_TYPE_TO_PLACE_MAP[self.terakoya_type],
            self.name,
            self.grade,
            self.arrival_time,
            self.terakoya_experience,
            self.study_subject,
            self.study_subject_detail,
            self.study_style,
            self.school_name,
            self.course_choice,
            self.future_free,
            self.like_thing_free,
            self.how_to_know_terakoya,
            self.remarks) for date in self.attendance_date_list]

    def send_confirmation_email(self) -> None:
        subject = "【カフェ塾テラコヤ】参加予約完了"
        body = f"""
            <p>{self.name}様</p>
            <p>カフェ塾テラコヤへの参加予約が完了致しました。</p>
            <p>予約内容は以下の通りです。</p>
            <br/>
            <p>参加区分: {self.TERAKOYA_TYPE_MAP[self.terakoya_type]}</p>
            <p>参加希望日: {",".join([DT.convert_iso_to_slushdate(dt) for dt in self.attendance_date_list])}</p>
            <p>来れそうな時間帯: {self.ARRIVAL_TIME_MAP[self.arrival_time]}</p>
            <p>テラコヤへの参加経験: {self.TERAKOYA_EXPERIENCE_MAP[self.terakoya_experience]}</p>
            <p>備考: {self.remarks}</p>
            <br/>
            {MAIL_BODY_CONTACT}
        """
        self.ses_client.send(self.email, subject, body, TERAKOYA_GROUP_MAIL_CC)

    def book(self) -> None:
        for bk_item in self.booking_item_list:
            print(f"Booking Item: {str(bk_item.__dict__)}")
            try:
                BookingDynamoDB.insert_item(bk_item)
            except Exception as e:
                print(f"Error happend. Error message: {str(e)}")
        self.send_confirmation_email()


def lambda_handler(event, context):
    try:
        # BookingViaSpreadsheet(event["body"]).book()
        BookingViaDynamoDB(event["body"]).book()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")


if __name__ == "__main__":
    spreadsheet_event_body = '{"name": "Test(I.G)", "email": "i.g.freetech2021@gmail.com", "terakoya_type": "カフェ塾テラコヤ(池袋)", "attendance_date_list": ["01/31 (火)", "02/07 (火)", "01/30 (月)"], "arrival_time": "17:00前", "grade": "その他", "terakoya_experience": "過去に参加したことがある", "study_subject": "社会", "study_subject_detail": "勉強したい科目の詳細", "study_style": "その他", "school_name": "XX学校", "course_choice": "文系", "future_free": "将来の夢・目標", "like_thing_free": "好きなこと・もの", "how_to_know_terakoya": "知人の紹介", "remarks": "備考"}'
    BookingViaSpreadsheet(spreadsheet_event_body).book()
    dynamodb_event_body = '''
    {
        "name": "Test",
        "email": "laughingman2045.sac@gmail.com",
        "terakoya_type": 0,
        "attendance_date_list": ["2023-01-31", "2023-02-07", "2023-02-14"],
        "arrival_time": 0,
        "grade": 11,
        "terakoya_experience": 1,
        "study_subject": 4,
        "study_subject_detail": "勉強したい内容について詳しく(自由記入)",
        "study_style": 3,
        "school_name": "学校名(自由記入)",
        "course_choice": 0,
        "future_free": "将来の夢など(自由記入)",
        "like_thing_free": "好きなこと(自由記入)",
        "how_to_know_terakoya": 1,
        "remarks": "備考(自由記入)"
    }
    '''
    BookingViaDynamoDB(dynamodb_event_body).book()
