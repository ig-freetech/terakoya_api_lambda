import os
import sys
import json
from typing import List, Dict

ROOT_DIR_PATH = os.path.dirname(__file__)
sys.path.append(ROOT_DIR_PATH)

from utils.dt import CURRENT_DATETIME
from utils.spreadsheet import append_row_to_sheet, get_system_future_records, get_main_future_records
from utils.mail import connect_gmail_server, close_gmail_server, send_email

TERAKOYA_TYPE_PLACE_DICT: Dict[str, str] = {
    "カフェ塾テラコヤ(池袋)": "",
    "オンラインテラコヤ(多摩)": "キャリア・マム",
    "テラコヤ中等部(池袋)": "サンシャインシティ",
    "テラコヤ中等部(渋谷)": "キカガク"
}

COMPLETE_MAIL_SUBJECT = "参加予約完了"

MAIN_SHEET_TIMESTAMP_FORMAT = f"%Y/%m/%d %H:%M:%S"


class Record:
    name: str = ""
    email: str = ""
    terakoya_type: str = ""
    attendance_date_list: List[str] = []
    arrive_time: str = ""
    grade: str = ""
    terakoya_experience: str = ""
    study_subject: str = ""
    study_subject_details: str = ""
    study_method: str = ""
    school_name: str = ""
    course_choice: str = ""
    future_free: str = ""
    like_free: str = ""
    how_to_know_terakoya: str = ""
    remarks: str = ""


def get_record_from_response_body(event_body) -> Record:
    body_dic = json.loads(event_body)
    record = Record()
    record.name = body_dic["name"]
    record.email = body_dic["email"]
    record.terakoya_type = body_dic["terakoyaType"]
    record.attendance_date_list = body_dic["attendanceDate"]
    record.arrive_time = body_dic["arriveTime"]
    record.grade = body_dic["grade"]
    record.terakoya_experience = body_dic["terakoyaExperience"]
    record.study_subject = body_dic["studySubject"]
    record.study_subject_details = body_dic["studySubjectDetail"]
    record.study_method = body_dic["studyMethod"]
    record.school_name = body_dic["schoolName"]
    record.course_choice = body_dic["courseChoice"]
    record.future_free = body_dic["futureFree"]
    record.like_free = body_dic["likeFree"]
    record.how_to_know_terakoya = body_dic["howToKnowTerakoya"]
    record.remarks = body_dic["remarks"]
    return record


def exists_record(record: Record, attendance_date: str):
    future_system_records = get_system_future_records()
    searched_records = [rec for rec in future_system_records
                        if rec["参加日"] == attendance_date
                        and rec["メールアドレス"] == record.email
                        and rec["参加希望"] == record.terakoya_type
                        ]
    return len(searched_records) > 0


def exists_main_record(record: Record):
    future_main_records = get_main_future_records()
    # for rec in future_main_records:
    #     main_attend_date_list = rec["参加希望日"].split(",")
    #     symmetric_difference = set(main_attend_date_list) ^ set(record.attendance_date_list)
    #     symmetric_difference_list = list(symmetric_difference)
    searched_records = [rec for rec in future_main_records
                        if len(list(set(rec["参加希望日"].split(",")) ^ set(record.attendance_date_list))) == 0
                        and rec["メールアドレス"] == record.email
                        and rec["参加希望"] == record.terakoya_type
                        ]
    return len(searched_records) > 0


def record_to_system(record: Record):
    for attendance_date in record.attendance_date_list:
        if(exists_record(record=record, attendance_date=attendance_date)):
            print(
                f"{record.email},{attendance_date},{record.terakoya_type} is already registered in System Sheet.")
            continue
        append_row_to_sheet(sheet_type="system", row=[
            record.name,
            record.email,
            attendance_date,
            record.terakoya_type,
            TERAKOYA_TYPE_PLACE_DICT[record.terakoya_type]
        ])


def record_to_main(record: Record):
    dt_jst = CURRENT_DATETIME.strftime(MAIN_SHEET_TIMESTAMP_FORMAT)
    if(exists_main_record(record=record)):
        print(
            f"{record.email},{record.attendance_date_list},{record.terakoya_type} is already registered in Main Sheet.")
        return
    append_row_to_sheet(sheet_type="main", row=[
        dt_jst,
        record.name,
        record.terakoya_type,
        record.arrive_time,
        record.grade,
        ",".join(record.attendance_date_list),
        record.terakoya_experience,
        record.study_subject,
        record.study_subject_details,
        record.study_method,
        record.school_name,
        record.course_choice,
        record.future_free,
        record.like_free,
        record.how_to_know_terakoya,
        record.email,
        record.remarks
    ])


def make_mail_body(record: Record) -> str:
    body = f"""
        <p>{record.name}様</p>
        <p>カフェ塾テラコヤへの参加予約が完了致しました。</p>
        <p>予約内容は以下の通りです。</p>
        <br/>
        <p>参加区分: {record.terakoya_type}</p>
        <p>参加希望日: {",".join(record.attendance_date_list)}</p>
        <p>来れそうな時間帯: {record.arrive_time}</p>
        <p>テラコヤへの参加経験: {record.terakoya_experience}</p>
        <p>備考: {record.remarks}</p>
        <br/>
    """
    return body


def send_complete_mail(record: Record):
    connect_gmail_server()
    body = make_mail_body(record)
    send_email(mail_address_to=record.email,
               subject=COMPLETE_MAIL_SUBJECT, body_main=body)
    close_gmail_server()


def lambda_handler(event, context):
    try:
        record = get_record_from_response_body(event["body"])
        print("record is " + str(record.__dict__))
        record_to_system(record)
        record_to_main(record)
        send_complete_mail(record)
        print("Finished Reservation Registration.")
    except Exception as e:
        print("Error Happend:\n")
        print(e)


def test():
    # body = '{"grade":"中学1年生","arriveTime":"17:00前","courseChoice":"","studySubject":"キャリア説明会","studyMethod":"黙々と静かに勉強したい","howToKnowTerakoya":"Instagram","terakoyaType":"テラコヤ中等部(池袋)","schoolName":"","futureFree":"","likeFree":"","name":"池田元気","email":"i.g.freetech2021@gmail.com","attendanceDate":["7/2 (土)","7/9 (土)","7/16 (土)"],"terakoyaExperience":"過去に参加したことがある","studySubjectDetail":"","remarks":""}'
    # body = '{"grade":"中学1年生","arriveTime":"17:00前","courseChoice":"","studySubject":"キャリア説明会","studyMethod":"黙々と静かに勉強したい","howToKnowTerakoya":"Instagram","terakoyaType":"カフェ塾テラコヤ(池袋)","schoolName":"","futureFree":"","likeFree":"","name":"池田元気","email":"i.g.freetech2021@gmail.com","attendanceDate":["7/9 (土)","7/2 (土)","7/23 (土)"],"terakoyaExperience":"過去に参加したことがある","studySubjectDetail":"","remarks":"菅原さんと一緒がいい"}'
    body = '{"grade":"中学1年生","arriveTime":"17:00前","courseChoice":"","studySubject":"キャリア説明会","studyMethod":"黙々と静かに勉強したい","howToKnowTerakoya":"Instagram","terakoyaType":"カフェ塾テラコヤ(池袋)","schoolName":"","futureFree":"","likeFree":"","name":"池田元気","email":"i.g.freetech2021@gmail.com","attendanceDate":["7/2 (土)","7/9 (土)","7/23 (土)"],"terakoyaExperience":"過去に参加したことがある","studySubjectDetail":"","remarks":"菅原さんと一緒がいい"}'
    record = get_record_from_response_body(body)
    print("rec is " + str(record.__dict__))
    record_to_system(record)
    record_to_main(record)
    send_complete_mail(record)
    print('end')


if __name__ == "__main__":
    test()
