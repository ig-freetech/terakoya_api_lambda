from utils.dt import convert_to_datetime, calc_two_dates_diff_days, CURRENT_DATETIME
from utils.spreadsheet import get_system_future_records, find_cell_address, update_cell
from utils import mail
from datetime import datetime
import requests
from typing import List, Dict


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

FUTURE_SYSTEM_RECORDS = get_system_future_records()

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
    headers = {"content-type": "application/json"}
    response = requests.get(SHEET_URL, headers=headers)
    data = response.json()
    values = data['values']
    resStudentInfoList: List[List[str]] = values[1:]  # カラム行を除いた2行目から取得

    studentInfoList = []
    for filteredStudentInfo in [resStudentInfo for resStudentInfo in resStudentInfoList if len(resStudentInfo) != REMIND_MAIL_ALREADY_SENT_COLUMN_NUMBER]:
        studentInfo = StudentInfo()
        studentInfo.name = filteredStudentInfo[0]
        studentInfo.original_reserved_date = filteredStudentInfo[2]
        studentInfo.reserved_datetime = convert_to_datetime(
            filteredStudentInfo[2])
        studentInfo.email = filteredStudentInfo[1]
        studentInfo.terakoya_type = filteredStudentInfo[3]
        studentInfo.place = filteredStudentInfo[4]
        studentInfoList.append(studentInfo)

    return studentInfoList


def update_already_remind_mail_column(studentInfo: StudentInfo):
    search_words = [studentInfo.email, studentInfo.original_reserved_date,
                    studentInfo.terakoya_type, studentInfo.place]
    cell_address = find_cell_address(
        search_words=search_words, column_name=ALREADY_REMIND_MAIL_COLUMN_NAME)
    update_cell(cell_address=cell_address, value=ALREADY_REMIND_MAIL_VALUE)


def send_remind_mail_list(studentInfoList: List[StudentInfo]):
    mail.connect_gmail_server()
    for studentInfo in studentInfoList:
        if(should_send_email(studentInfo.reserved_datetime)):
            subject = 'ご参加当日のお知らせ'  # 件名
            body_main = f'''
                <p>{studentInfo.name}様</p>
                <p>カフェ塾テラコヤへの参加予約ありがとうございました。</p>
                <p>ご予約の当日となりましたので、お知らせ申し上げます。</p>
                <p>本日は、{studentInfo.place}にお越し下さい。</p>
            '''  # 本文
            img_file_name = SUNSHINE_MAP_IMG_FILE_NAME if studentInfo.place == "サンシャインシティ" else None
            mail.send_email(mail_address_to=studentInfo.email,
                            subject=subject, body_main=body_main, body_footer=PLACE_DICT[studentInfo.place], img_file_name=img_file_name)
            update_already_remind_mail_column(studentInfo=studentInfo)
        else:
            continue
    mail.close_gmail_server()


def should_send_email(reserved_datetime: datetime):
    diff_days = calc_two_dates_diff_days(reserved_datetime, CURRENT_DATETIME)
    return diff_days == 0  # 日時差分が1日以内ならばメール送信の必要あり


def main():
    try:
        studentInfoList = get_student_info_list()
        send_remind_mail_list(studentInfoList)
        print("Finished Sending Remind E-mails.")
    except Exception as e:
        print(e)


def lambda_handler(event, context):
    main()


if __name__ == '__main__':
    main()
