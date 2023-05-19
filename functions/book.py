import os
import sys
import json
from abc import ABCMeta, abstractmethod

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from domain.dynamodb import BookingDynamoDB, BookingItem

from utils.mail import SesMail
from utils.dt import DT
from utils.process import lambda_handler_wrapper, handle_exception

from conf.env import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS

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
        self.first_choice_school = request_body["first_choice_school"]
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
        0: 999,  # その他 -> NULL
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
            self.first_choice_school,
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
    # lambda args: return value (ex: lambda n: n * 2, lambda: "Hello World", lambda text: print(text))
    # https://qiita.com/nagataaaas/items/531b1fc5ce42a791c7df
    # lambda is anonymous function as arrow function in JavaScript but it can't be used to define a function more than two lines.
    # https://qiita.com/masaru/items/48ee394640400f0f0d1c
    lambda_handler_wrapper(event, lambda: BookingViaDynamoDB(event["body"]).book())
