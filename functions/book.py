import os
import sys
import json
from typing import Any, Dict

FUNCTIONS_DIR_PATH = os.path.dirname(__file__)
sys.path.append(FUNCTIONS_DIR_PATH)

from conf.env import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS
from domain.booking import BookingTable
from models.booking import ARRIVAL_TIME, TERAKOYA_EXPERIENCE, TERAKOYA_TYPE, BookRequestBody, BookingItem
from utils.mail import SesMail
from utils.dt import DT
from utils.process import lambda_handler_wrapper

TERAKOYA_GMAIL_FROM = "" if TERAKOYA_GMAIL_ADDRESS is None else TERAKOYA_GMAIL_ADDRESS
TERAKOYA_GROUP_MAIL_CC = "" if TERAKOYA_GROUP_MAIL_ADDRESS is None else TERAKOYA_GROUP_MAIL_ADDRESS


class BookingRequest:
    def __init__(self, book_request_body_json: Dict[str, Any]) -> None:
        book_request_body = BookRequestBody(**book_request_body_json)
        # **obj converts obj to kwargs to be able to combine with other kwargs as ...obj in TypeScript
        # https://www.koatech.info/blog/python-asterisk
        self.booking_item_list = [BookingItem(**{**book_request_body.dict(), "date": date})
                                  for date in book_request_body.attendance_date_list]
        # * Props for sending confirmation email
        self.__name = book_request_body.name
        self.__email = book_request_body.email
        self.__terakoya_type = book_request_body.terakoya_type
        self.__attendance_date_list = book_request_body.attendance_date_list
        self.__arrival_time = book_request_body.arrival_time
        self.__terakoya_experience = book_request_body.terakoya_experience
        self.__remarks = book_request_body.remarks

    def __send_confirmation_email(self) -> None:
        subject = "【カフェ塾テラコヤ】参加予約完了"
        TERAKOYA_TYPE_MAP: Dict[TERAKOYA_TYPE, str] = {
            TERAKOYA_TYPE.HIGH_IKE: 'カフェ塾テラコヤ(池袋)',
            TERAKOYA_TYPE.ONLINE_TAMA: 'オンラインテラコヤ(多摩)',
            TERAKOYA_TYPE.MID_IKE: 'テラコヤ中等部(池袋)',
            TERAKOYA_TYPE.MID_SHIBU: 'テラコヤ中等部(渋谷)',
        }
        ARRIVAL_TIME_MAP: Dict[ARRIVAL_TIME, str] = {
            ARRIVAL_TIME.BEFORE_1700: '17:00前',
            ARRIVAL_TIME.BETWEEN_1700_1730: '17:00~17:30',
            ARRIVAL_TIME.BETWEEN_1730_1800: '17:30~18:00',
            ARRIVAL_TIME.AFTER_1800: '18:00以降',
        }
        TERAKOYA_EXPERIENCE_MAP: Dict[TERAKOYA_EXPERIENCE, str] = {
            TERAKOYA_EXPERIENCE.FIRST_TIME: '今回が初回',
            TERAKOYA_EXPERIENCE.DONE: '過去に参加したことがある',
        }
        body = f"""
            <p>{self.__name}様</p>
            <p>カフェ塾テラコヤへの参加予約が完了致しました。</p>
            <p>予約内容は以下の通りです。</p>
            <br/>
            <p>参加区分: {TERAKOYA_TYPE_MAP[self.__terakoya_type]}</p>
            <p>参加希望日: {",".join([DT.convert_iso_to_slushdate(dt) for dt in self.__attendance_date_list])}</p>
            <p>来れそうな時間帯: {ARRIVAL_TIME_MAP[self.__arrival_time]}</p>
            <p>テラコヤへの参加経験: {TERAKOYA_EXPERIENCE_MAP[self.__terakoya_experience]}</p>
            <p>備考: {self.__remarks}</p>
            <br/>
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
        SesMail(TERAKOYA_GMAIL_FROM).send(self.__email, subject, body, TERAKOYA_GROUP_MAIL_CC)

    def book(self) -> None:
        for bk_item in self.booking_item_list:
            print(f"Booking Item: {str(bk_item.to_dict())}")
            try:
                BookingTable.insert_item(bk_item)
            except Exception as e:
                print(f"Error happend. Error message: {str(e)}")
        self.__send_confirmation_email()


def lambda_handler(event, context):
    return lambda_handler_wrapper(event, BookingRequest(json.loads(event["body"])).book)
