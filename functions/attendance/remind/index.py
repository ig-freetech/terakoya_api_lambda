from typing import List
import datetime
import re
import smtplib
from email.mime.text import MIMEText
import requests

# gmailアカウント
# TODO: Gmailアカウントはcsvか何かのテキストファイルに収めてクラウドストレージに保存し、スクリプトからはそのURLにGETしてアカウント情報を取得する形にする
gmail_account = "npoterakoya2021@gmail.com"
gmail_password = "ybgeiljfywqyfaqr"
# gmail_password = "h6g5f4d3"

gmail_smtp_host = "smtp.gmail.com" # GmailのSMTPサーバのホスト名は smtp.gmail.com となっている
gmail_smtp_ssl_port = 465 # GmailのSMTPサーバのSSLのポート番号は465となっている（TLSの場合は587）

SHEET_NAME = "system"

terakoya_group_mail_addr = "info@npoterakoya.org"

class ReservedDate:
    month = -1
    day = -1

class StudentInfo:
    name = ''
    reserved_date: ReservedDate
    email = ''
    terakoya_type = ''
    place = ''

def get_student_info_list() -> List[StudentInfo]:
    headers = {"content-type": "application/json"}
    response = requests.get(f"https://sheets.googleapis.com/v4/spreadsheets/1TFjUeVX36bSsGVoyRtFO1CJX8uVc52wAx6O2pvSbdUk/values/{SHEET_NAME}?key=AIzaSyCvhazrcQ92ov-kBa8HEZvkYYUO6rp2f6I", headers=headers)
    data = response.json()
    values = data['values']
    resStudentInfoList = values[1:] # カラム行を除いた2行目から取得

    studentInfoList = []
    for resStudentInfo in resStudentInfoList:
        studentInfo = StudentInfo()
        studentInfo.name = resStudentInfo[0]
        studentInfo.reserved_date = format_reserved_date(resStudentInfo[2])
        studentInfo.email = resStudentInfo[1]
        studentInfo.terakoya_type = resStudentInfo[3]
        studentInfo.place = resStudentInfo[4]
        studentInfoList.append(studentInfo)

    return studentInfoList

def format_reserved_date(dateStr):
    regDate = re.search(r'\d+/\d+', dateStr).group().split('/') # ['MM', 'DD'] の形で抽出
    reservedDate = ReservedDate()
    reservedDate.month = int(regDate[0])
    reservedDate.day = int(regDate[1])
    return reservedDate

def should_send_email(reservedDate: ReservedDate):
    currentDateTime = datetime.datetime.now()
    reservedDateTime = datetime.datetime(year=currentDateTime.year, month=reservedDate.month, day=reservedDate.day)
    diff = reservedDateTime - currentDateTime
    if diff.days < 1:
        # 日時差分が1日以内ならばメール送信の必要あり
        return True
    else:
        # 日時差分が1日以内の予約日が無い場合はメール送信の必要なし
        return False

def send_email(name: str, email: str, place: str):
    # メールの送信先
    mail_address_to = email

    # MIME（メールデータ）の作成
    subject = '【カフェ塾テラコヤ】参加日のご連絡' # 件名
    # HACK: メール本文はtxtファイルに保存して直下に置きopen関数で開く形で取得する
    body = f'''
        <div>
            <p>{name}様</p>
            <p>カフェ塾テラコヤへの参加予約ありがとうございました。</p>
            <p>ご予約の当日となりましたので、念のためお知らせ申し上げます。</p>
            <p>本日は、{place}にお越し下さい。</p>
            <p>お会いできますことを心よりお待ちしております。</p>
            <p>どうぞお気をつけてお越しくださいませ。</p>
            <p>塾長 前田</p>
            <p>＝＝＝＝＝＝＝連絡先＝＝＝＝＝＝＝＝</p>
            <p>電話番号：090-6543-0718</p>
            <p>メールアドレス：info@npoterakoya.org</p>
            <p>※予約キャンセルの場合やその他ご不明点等ありましたら公式LINEからご連絡下さい。</p>
            <p>＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝＝</p>
        </div>
        ''' # 本文
    msg = MIMEText(body, "html") # 第2引数にMIMEタイプのsubtypeを指定（typeは当然textに決まっている）
    # MIMETextに属性値をセットする
    msg["Subject"] = subject
    msg["To"] = mail_address_to # 送り先メールアドレスを設定
    msg["From"] =  gmail_account # 送り元メールアドレスを設定
    msg["Cc"] = terakoya_group_mail_addr # 生徒へのリマインドメール送信をテラコヤ運営メンバーのメールグループアドレスにも送信して通知

     # Gmailに接続
    gmail_smtp_server = smtplib.SMTP_SSL(gmail_smtp_host, gmail_smtp_ssl_port) # SMTPサーバホスト名とSSLポート番号を指定してサーバオブジェクト生成
    gmail_smtp_server.login(gmail_account, gmail_password) # Gmailにログインして接続
    gmail_smtp_server.send_message(msg) # MIMEを送信
    gmail_smtp_server.quit() # サーバから切断
    print("Sent a email")

    # TODO: Cannot authenticate due to temporary system problem というエラーが発生して止まりうるのでシートに送信済みフラグ列を作成して catch して全部送信するようにする

def main():
    studentInfoList = get_student_info_list()
    for studentInfo in studentInfoList:
        if(should_send_email(studentInfo.reserved_date)):
            send_email(studentInfo.name, studentInfo.email, studentInfo.place)
        else:
            continue        
    print("end")

def lambda_handler(event, context):
    main()

if __name__ == '__main__':
    main()