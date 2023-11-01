import os
import sys
from typing import Dict

FUNCTIONS_DIR_PATH = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
sys.path.append(FUNCTIONS_DIR_PATH)

from conf.env import TERAKOYA_GMAIL_ADDRESS, TERAKOYA_GROUP_MAIL_ADDRESS
from domain.booking import BookingTable
from models.booking import TERAKOYA_TYPE, PLACE
from utils.process import lambda_handler_wrapper
from utils.mail import SesMail


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

PLACE_DICT = {
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
        <p>初回参加の方や17:00以降に到着される場合はご案内致しますので公式LINEからご連絡下さい。</p>
        <p>よろしくお願いします。</p>
    """,
    "テラコヤ事務所（ベースキャンプ）": """
        <p>■テラコヤ事務所（ベースキャンプ）</p>
        <p>(池袋駅C3出口から徒歩3分)</p>
        <p>〒171-0021</p>
        <p>東京都豊島区西池袋５丁目１０−２４</p>
        <p>※建物の1階部分です。</p>
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


class Remind():
    __ses_client = SesMail(TERAKOYA_GMAIL_FROM)

    # booking_date, terakoya_type are used only for spreadsheet
    def __init__(self, name: str, place: str, email: str, booking_date: str = "", terakoya_type: str = "") -> None:
        self.name = name
        self.place = place
        self.email = email
        self.booking_date = booking_date
        self.terakoya_type = terakoya_type

    def send_remind_mail(self) -> None:
        subject = '【カフェ塾テラコヤ】ご参加当日のお知らせ'
        body = f"""
            <p>{self.name}様</p>
            <p>カフェ塾テラコヤへの参加予約ありがとうございました。</p>
            <p>ご予約の当日となりましたので、お知らせ申し上げます。</p>
            <p>本日は、{self.place}にお越し下さい。</p>
            <p>住所の詳細等につきましては本メール下部に記載しておりますので、ご確認下さい。</p>
            <br/>
            {MAIL_BODY_CONTACT}
            <br/>
            {PLACE_DICT[self.place]}
        """
        PLACE_TO_IMG = {
            "サンシャインシティ": "sunshine-map.jpg",
            "テラコヤ事務所（ベースキャンプ）": "base-camp-exterior.png",
        }
        img_fpath = os.path.join(FUNCTIONS_DIR_PATH, "assets", PLACE_TO_IMG.get(self.place, ""))

        self.__ses_client.send(self.email, subject, body, TERAKOYA_GROUP_MAIL_CC, img_fpath)


def remind() -> None:
    # Map定義
    # https://terakoya20220112.slack.com/archives/C02V0PHDGP2/p1675009220056179
    PLACE_MAP: Dict[PLACE, str] = {
        PLACE.TBD: "",  # 未設定状態
        PLACE.SUNSHINE: "サンシャインシティ",
        PLACE.RYOHIN: "良品計画本社",
        PLACE.BASE_CAMP: "テラコヤ事務所（ベースキャンプ）",
        PLACE.CAREER_MOM: "キャリア・マム",
        PLACE.KIKAGAKU: "キカガク"
    }

    bk_item_list = BookingTable.get_item_list_for_remind()
    for bk_item in bk_item_list:
        print(f"Booking Item: {str(bk_item.__dict__)}")
        try:
            if (bk_item.terakoya_type == TERAKOYA_TYPE.HIGH_IKE and bk_item.place == PLACE.TBD):
                print("Impossible to send a email because of no place filled in Ikebukuro")
                continue
            Remind(bk_item.name, PLACE_MAP[bk_item.place], bk_item.email).send_remind_mail()
            BookingTable.update_is_reminded(bk_item.sk)
        except Exception as e:
            print(f"Error happend. Error message: {str(e)}")


def lambda_handler(event, context):
    print(f"event: {str(event)}")
    # AWS_LAMBDA_FUNCTION_NAME is the function name of the current function
    # https://docs.aws.amazon.com/ja_jp/lambda/latest/dg/configuration-envvars.html#configuration-envvars-runtime
    return lambda_handler_wrapper(event, remind, os.environ['AWS_LAMBDA_FUNCTION_NAME'])
