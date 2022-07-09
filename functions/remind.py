import os
import sys
from datetime import datetime
from typing import List, Dict

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from utils.dt import convert_to_datetime, calc_two_dates_diff_days, CURRENT_DATETIME
from utils.spreadsheet import get_system_future_records, find_cell_address, update_cell
from utils.mail import close_gmail_server, send_email

SHEET_NAME = "system"
SHEET_URL = f"https://sheets.googleapis.com/v4/spreadsheets/1TFjUeVX36bSsGVoyRtFO1CJX8uVc52wAx6O2pvSbdUk/values/{SHEET_NAME}?key=AIzaSyCvhazrcQ92ov-kBa8HEZvkYYUO6rp2f6I"
SUNSHINE_MAP_IMG_FILE_NAME = "sunshine-map.jpg"

PLACE_DICT: Dict[str, str] = {
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
        <p>17:00以降に来られる場合は、到着しましたら公式LINEからご連絡下さい。</p>
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

REMIND_MAIL_ALREADY_SENT_COLUMN_NUMBER = 6

ALREADY_REMIND_MAIL_COLUMN_NAME = "リマインドメール送信済み"
ALREADY_REMIND_MAIL_VALUE = "済"


class StudentInfo:
    name = ''
    original_reserved_date = ''
    reserved_datetime: datetime
    email = ''
    terakoya_type = ''
    place = ''


def get_student_info_list() -> List[StudentInfo]:
    future_system_records = get_system_future_records()
    print(f"(Post-dating records counts: {len(future_system_records)}) Post-dating records are below:")
    print("\n".join(map(lambda x: str(x), future_system_records)))
    filtered_student_info_list = [res_student_info for res_student_info in future_system_records if
                                  res_student_info["リマインドメール送信済み"] != "済"]
    print(
        f"(Post-dating unsent e-mail records counts: {len(filtered_student_info_list)}) Post-dating unsent e-mail records are below:")
    print("\n".join(map(lambda x: str(x), filtered_student_info_list)))

    student_info_list = []
    for filtered_student_info in filtered_student_info_list:
        student_info = StudentInfo()
        student_info.name = filtered_student_info["名前"]
        student_info.original_reserved_date = filtered_student_info["参加日"]
        student_info.reserved_datetime = convert_to_datetime(
            filtered_student_info["参加日"])
        student_info.email = filtered_student_info["メールアドレス"]
        student_info.terakoya_type = filtered_student_info["参加希望"]
        student_info.place = filtered_student_info["拠点"]
        student_info_list.append(student_info)

    return student_info_list


def update_already_remind_mail_column(student_info: StudentInfo):
    search_words = [student_info.email, student_info.original_reserved_date,
                    student_info.terakoya_type, student_info.place]
    cell_address = find_cell_address(
        search_words=search_words, column_name=ALREADY_REMIND_MAIL_COLUMN_NAME)
    update_cell(cell_address=cell_address, value=ALREADY_REMIND_MAIL_VALUE)


def send_remind_mail_list(student_info_list: List[StudentInfo]):
    for student_info in student_info_list:
        print("(Check whether to send a e-mail) StudentInfo: " + str(student_info.__dict__))
        if(should_send_email(student_info.reserved_datetime)):
            print("Should send a e-mail.")
            if(student_info.terakoya_type == "カフェ塾テラコヤ(池袋)" and student_info.place == ''):
                print(f"Place in Ikebukuro is not filled.")
                continue
            subject = 'ご参加当日のお知らせ'  # 件名
            body_main = f'''
                <p>{student_info.name}様</p>
                <p>カフェ塾テラコヤへの参加予約ありがとうございました。</p>
                <p>ご予約の当日となりましたので、お知らせ申し上げます。</p>
                <p>本日は、{student_info.place}にお越し下さい。</p>
                <p>住所の詳細等につきましては本メール下部に記載しておりますので、ご確認下さい。</p>
            '''  # 本文
            img_file_name = SUNSHINE_MAP_IMG_FILE_NAME if student_info.place == "サンシャインシティ" else None
            send_email(mail_address_to=student_info.email,
                       subject=subject, body_main=body_main, body_footer=PLACE_DICT[student_info.place], img_file_name=img_file_name)
            update_already_remind_mail_column(student_info=student_info)
        else:
            continue
    close_gmail_server()


def should_send_email(reserved_datetime: datetime):
    diff_days = calc_two_dates_diff_days(reserved_datetime, CURRENT_DATETIME)
    print(f"Dates difference is {str(diff_days)} day(s).")
    return diff_days == 0  # 日時差分が1日以内ならばメール送信の必要あり
    # return -2 < diff_days < 2  # 日時差分が前後2日以内 (test)


def main():
    try:
        student_info_list = get_student_info_list()
        send_remind_mail_list(student_info_list)
        print("Finished sending remind e-mails.")
    except Exception as e:
        print("Error happend. Error message: " + str(e))


def lambda_handler(event, context):
    main()


if __name__ == '__main__':
    main()
