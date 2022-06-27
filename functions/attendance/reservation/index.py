import os
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import datetime

KEY_FILE_PATH = os.path.join(os.path.dirname(__file__), "config", "gcp_service_account_key_terakoya-dev.json")
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
credentials = ServiceAccountCredentials.from_json_keyfile_name(KEY_FILE_PATH, scope)
client = gspread.authorize(credentials)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1TFjUeVX36bSsGVoyRtFO1CJX8uVc52wAx6O2pvSbdUk/edit#gid=306935450"
spread_sheet = client.open_by_url(SHEET_URL)

SYSTEM_SHEET = "system"
MAIN_SHEET = "参加予約_system"

system_sheet = spread_sheet.worksheet(SYSTEM_SHEET)
main_sheet = spread_sheet.worksheet(MAIN_SHEET)

def main(event, context):
    body_dic = json.loads(event["body"])
    print(body_dic)
    record_to_system(body_dic)
    record_to_main(body_dic)
    print("end")
    return {
    }

def record_to_system(body_dic):
    name = body_dic["name"]
    email = body_dic["email"]
    terakoya_type = body_dic["terakoyaType"]
    attendance_date_list = body_dic["attendanceDate"]
    for attendance_date in attendance_date_list:
        system_sheet.append_row([name, email, attendance_date, terakoya_type])

def record_to_main(body_dic):
    dt_jst = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=9))).strftime(f"%Y/%m/%d %H:%M:%S")
    print(dt_jst)
    name = body_dic["name"]
    terakoya_type = body_dic["terakoyaType"]
    arriveTime = body_dic["arriveTime"]
    grade = body_dic["grade"]
    attendanceDate = ",".join(body_dic["attendanceDate"])
    terakoyaExperience = body_dic["terakoyaExperience"]
    studySubject = body_dic["studySubject"]
    studySubjectDetail = body_dic["studySubjectDetail"]
    studyMethod = body_dic["studyMethod"]
    schoolName = body_dic["schoolName"]
    courseChoice = body_dic["courseChoice"]
    futureFree = body_dic["futureFree"]
    likeFree = body_dic["likeFree"]
    howToKnowTerakoya = body_dic["howToKnowTerakoya"]
    email = body_dic["email"]
    main_sheet.append_row([dt_jst, name, terakoya_type, arriveTime, grade, attendanceDate, terakoyaExperience, studySubject, studySubjectDetail, studyMethod, schoolName, courseChoice, futureFree, likeFree, "", "", howToKnowTerakoya, email])

def test():
    body = '{"grade":"その他","arriveTime":"17:00前","courseChoice":"理系","studySubject":"数学","studyMethod":"1人では難しいのでスタッフ付きっ切りで勉強を教えて欲しい","HowToKnowTerakoya":"その他","name":"池田元気","email":"i.g.freetech2021@gmail.com","terakoyaType":"カフェ塾テラコヤ（池袋）","attendanceDate":["6/21 (火)","6/28 (火)","7/5 (火)"],"terakoyaExperience":"過去に参加したことがある","schoolName":"テラコヤ運営チーム","studySubjectDetail":"巡回セールスマン問題","futureFree":"ポケモンマスター","likeFree":"女の子"}'
    body_dic = json.loads(body)
    record_to_system(body_dic)
    record_to_main(body_dic)

if __name__ == "__main__":
    test()
