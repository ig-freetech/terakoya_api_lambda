import os
import sys
import json
from abc import ABCMeta, abstractmethod

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from utils.mail import SesMail
from utils.dt import current_jst_datetime, convert_to_datetime
from utils.spreadsheet import Spreadsheet

from config.mail_config import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS
from config.google_config import TERAKOYA_SPREADSHEET_URL

TERAKOYA_GMAIL_FROM = "" if TERAKOYA_GMAIL_ADDRESS is None else TERAKOYA_GMAIL_ADDRESS
TERAKOYA_GROUP_MAIL_CC = "" if TERAKOYA_GROUP_MAIL_ADDRESS is None else TERAKOYA_GROUP_MAIL_ADDRESS

TERAKOYA_TYPE_PLACE_DICT = {
    "カフェ塾テラコヤ(池袋)": "",
    "オンラインテラコヤ(多摩)": "キャリア・マム",
    "テラコヤ中等部(池袋)": "サンシャインシティ",
    "テラコヤ中等部(渋谷)": "キカガク"
}

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
    __ses_client = SesMail(TERAKOYA_GMAIL_FROM)

    def __init__(self, event_body) -> None:
        request_body = json.loads(event_body)
        self.name = request_body["name"]
        self.email = request_body["email"]
        self.terakoya_type = request_body["terakoyaType"]
        self.attendance_date_list = request_body["attendanceDateList"]
        self.arrive_time = request_body["arriveTime"]
        self.grade = request_body["grade"]
        self.terakoya_experience = request_body["terakoyaExperience"]
        self.study_subject = request_body["studySubject"]
        self.study_subject_detail = request_body["studySubjectDetail"]
        self.study_method = request_body["studyMethod"]
        self.school_name = request_body["schoolName"]
        self.course_choice = request_body["courseChoice"]
        self.future_free = request_body["futureFree"]
        self.like_free = request_body["likeFree"]
        self.how_to_know_terakoya = request_body["howToKnowTerakoya"]
        self.remarks = request_body["remarks"]

    def send_confirmation_email(self) -> None:
        subject = "【カフェ塾テラコヤ】参加予約完了"
        body = f"""
            <p>{self.name}様</p>
            <p>カフェ塾テラコヤへの参加予約が完了致しました。</p>
            <p>予約内容は以下の通りです。</p>
            <br/>
            <p>参加区分: {self.terakoya_type}</p>
            <p>参加希望日: {",".join(self.attendance_date_list)}</p>
            <p>来れそうな時間帯: {self.arrive_time}</p>
            <p>テラコヤへの参加経験: {self.terakoya_experience}</p>
            <p>備考: {self.remarks}</p>
            <br/>
            {MAIL_BODY_CONTACT}
        """
        self.__ses_client.send(self.email, subject, body, TERAKOYA_GROUP_MAIL_CC)

    @abstractmethod
    def book(self) -> None:
        raise NotImplementedError()


class BookingSpreadsheet(IBooking):
    """
    NOTE: change main and system's sheet name to another one to test
    """
    __spread_sheet = Spreadsheet(TERAKOYA_SPREADSHEET_URL)
    # __main_sheet = __spread_sheet.get_worksheet("参加予約_system")
    # __system_sheet = __spread_sheet.get_worksheet("system")
    __main_sheet = __spread_sheet.get_worksheet("main_test")
    __system_sheet = __spread_sheet.get_worksheet("system_test")

    def __record_to_main(self):
        dt_jst = current_jst_datetime.strftime(MAIN_SHEET_TIMESTAMP_FORMAT)
        print(f"Record: {self.email},{self.attendance_date_list},{self.terakoya_type}")
        if (self.__exists_record_in_main()):
            print("Already registered in Main")
            return
        self.__main_sheet.append_row([
            dt_jst,
            self.name,
            self.terakoya_type,
            self.arrive_time,
            self.grade,
            ",".join(self.attendance_date_list),
            self.terakoya_experience,
            self.study_subject,
            self.study_subject_detail,
            self.study_method,
            self.school_name,
            self.course_choice,
            self.future_free,
            self.like_free,
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
                TERAKOYA_TYPE_PLACE_DICT[self.terakoya_type]
            ])

    def __exists_record_in_main(self):
        records_after_today = [rec for rec in self.__main_sheet.get_all_records() if len(
            [x for x in rec["参加希望日"].split(",") if convert_to_datetime(x) > current_jst_datetime]) > 0]
        same_records = [rec for rec in records_after_today
                        if len(list(set(rec["参加希望日"].split(",")) ^ set(self.attendance_date_list))) == 0
                        and rec["メールアドレス"] == self.email
                        and rec["参加希望"] == self.terakoya_type
                        ]
        return len(same_records) > 0

    def __exists_record_in_system(self, attendance_date: str):
        records_after_today = [rec for rec in self.__system_sheet.get_all_records() if rec["メールアドレス"] != '' and convert_to_datetime(
            rec["参加日"]) > current_jst_datetime]
        searched_records = [rec for rec in records_after_today
                            if rec["参加日"] == attendance_date
                            and rec["メールアドレス"] == self.email
                            and rec["参加希望"] == self.terakoya_type
                            ]
        return len(searched_records) > 0

    def book(self) -> None:
        print(f"Record: {str(self.__dict__)}")
        self.__record_to_main()
        self.__record_to_system()
        self.send_confirmation_email()
        print("Record completed!")


def lambda_handler(event, context):
    try:
        booking_spreadsheet = BookingSpreadsheet(event)
        booking_spreadsheet.book()
    except Exception as e:
        print(f"Error happend. Error message: {str(e)}")


if __name__ == "__main__":
    event_body = '{"name": "Test(I.G)", "email": "i.g.freetech2021@gmail.com", "terakoyaType": "テラコヤ中等部(池袋)", "attendanceDateList": ["01/31 (火)", "02/07 (火)", "01/30 (月)"], "arriveTime": "17:00前", "grade": "その他", "terakoyaExperience": "過去に参加したことがある", "studySubject": "社会", "studySubjectDetail": "", "studyMethod": "その他", "schoolName": "", "courseChoice": "", "futureFree": "", "likeFree": "", "howToKnowTerakoya": "知人の紹介", "remarks": "一応、スタッフとして入ってます笑。"}'
    booking_spreadsheet = BookingSpreadsheet(event_body)
    booking_spreadsheet.book()
