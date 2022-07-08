from time import sleep
from typing import Union
from utils.file import get_dic_from_json
import os
import sys
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.policy import SMTPUTF8

ROOT_DIR_PATH = os.path.dirname(os.path.dirname(__file__))
sys.path.append(ROOT_DIR_PATH)

ASSETS_DIR_PATH = os.path.join(ROOT_DIR_PATH, "assets")

TERAKOYA_GMAIL_ACCOUNT_INFO_FPATH = os.path.join(
    ROOT_DIR_PATH, "config", "terakoya_gmail_account_info.json")
account_info = get_dic_from_json(TERAKOYA_GMAIL_ACCOUNT_INFO_FPATH)
gmail_account = account_info["mail"]
gmail_password = account_info["pw"]

gmail_smtp_host = "smtp.gmail.com"  # GmailのSMTPサーバのホスト名は smtp.gmail.com となっている
# gmail_smtp_port = 587  # GmailのSMTPサーバのTLSのポート番号は587
gmail_smtp_ssl_port = 465  # GmailのSMTPサーバのSSLのポート番号は465
# SMTPサーバホスト名とSSLポート番号を指定してサーバオブジェクト生成
# gmail_smtp_server = smtplib.SMTP(gmail_smtp_host, gmail_smtp_port)
gmail_smtp_server = smtplib.SMTP_SSL(gmail_smtp_host, gmail_smtp_ssl_port)

TERAKOYA_GROUP_MAIL_ADDRESS = "info@npoterakoya.org"

MAIL_SUBJECT_COMMON = "【カフェ塾テラコヤ】"

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
    <br/>
"""

def close_gmail_server():
    gmail_smtp_server.quit()  # サーバから切断


def get_mime_img(img_file_name: str) -> MIMEImage:
    mime_image: MIMEImage
    with open(os.path.join(ASSETS_DIR_PATH, img_file_name), "rb") as f:
        mime_image = MIMEImage(f.read(), name=img_file_name)
    return mime_image

def send_msg(msg: MIMEMultipart):
    print("Try to send a message")
    try:
        gmail_smtp_server.send_message(msg)
    except Exception as e:
        print(e)
        sleep(3000)
        send_msg(msg)


def send_email(mail_address_to: str, subject: str, body_main: str, body_footer: str = "", img_file_name: Union[str, None] = None):
    msg = MIMEMultipart()
    body = f"""
        <div>
            <br/>
            {body_main}
            {MAIL_BODY_CONTACT}
            {body_footer}
        </div>
    """
    body_mime_text = MIMEText(body, "html", policy=SMTPUTF8)
    msg.attach(body_mime_text)
    if(img_file_name):
        mime_img = get_mime_img(img_file_name)
        msg.attach(mime_img)  # 画像ファイル添付
    msg["Subject"] = MAIL_SUBJECT_COMMON + subject  # 件名を設定
    msg["To"] = mail_address_to  # 送り先メールアドレスを設定
    msg["From"] = gmail_account  # 送り元メールアドレスを設定
    # 生徒へのメール送信をテラコヤ運営メンバーのメールグループアドレスにも送信して通知
    msg["Cc"] = TERAKOYA_GROUP_MAIL_ADDRESS

    gmail_smtp_server.login(gmail_account, gmail_password)
    send_msg(msg)
      # メールを送信
    print("Sent a email")


if __name__ == "__main__":
    print("test")
