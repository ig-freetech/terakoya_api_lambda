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
        <p>東京都多摩市落合1-46-1 ココリア多摩センター7階</p>
        <p>http://www.c-mam.co.jp/oshigoto_cafe/</p>
    """,
    "ひばりヶ丘校": """
        <p>■ひばりヶ丘校住所</p>
        <p>〒202-0001</p>
        <p>東京都西東京市ひばりヶ丘1-4-27</p>
    """,
    "神田校": """
        <p>■神田校住所</p>
        <p>〒101-0047</p>
        <p>東京都千代田区神田2丁目16-8</p>
        <p>古河電工神田ビル8階</p>
    """,
    "長沢校": """
        <p>■長沢校住所</p>
        <p>〒999-4605</p>
        <p>山形県最上郡舟形町長沢1072</p>
    """,
    "長南校": """
        <p>■長南校住所</p>
        <p>〒297-0121</p>
        <p>千葉県長生郡長南町長南770-1</p>
    """,
    "谷口校": """
        <p>■谷口校住所</p>
        <p>〒930-3222</p>
        <p>富山県中新川郡立山町谷口43</p>
    """,
    "芦田校": """
        <p>■芦田校住所</p>
        <p>〒669-3804</p>
        <p>兵庫県丹波市青垣町田井縄371<p>
    """,
    "忠海校": """
        <p>■忠海校住所</p>
        <p>〒729-2317</p>
        <p>広島県竹原市忠海東町5-19-1</p>
    """,
    "土肥校": """
        <p>■土肥校住所</p>
        <p>■〒410-3302</p>
        <p>静岡県伊豆市土肥638</p>
    """,
    "泊川校": """
        <p>■泊川校住所</p>
        <p>〒043-0334</p>
        <p>北海道二海郡八雲町熊石泊川町236</p>
    """,
    "菅田校": """
        <p>■菅田校住所</p>
        <p>〒509-1623</p>
        <p>岐阜県下呂市金山町菅田桐洞117</p>
    """,
    "山守校": """
        <p>■山守校住所</p>
        <p>〒682-0422</p>
        <p>鳥取県倉吉市関金町堀2163</p>
    """,
    "片田校": """
        <p>■片田校住所</p>
        <p>〒324-0223</p>
        <p>栃木県大田原市片田973</p>
    """,
    "中松校": """
        <p>■中松校住所</p>
        <p>〒869-1505</p>
        <p>熊本県阿蘇郡南阿蘇村中松4212<p>
    """,
    "中津原校": """
        <p>■中津原校住所</p>
        <p>〒822-1405</p>
        <p>福岡県田川郡香春町中津原812</p>
    """,
    "長若校": """
        <p>■長若校住所</p>
        <p>〒368-0103</p>
        <p>埼玉県秩父郡小鹿野町般若902</p>
    """,
    "外丸校": """
        <p>■外丸校住所</p>
        <p>〒949-8206</p>
        <p>新潟県中魚沼郡津南町外丸丙1174</p>
    """,
    "上ノ加江校": """
        <p>■上ノ加江校住所</p>
        <p>〒789-1302</p>
        <p>高知県高岡郡中土佐町上ノ加江5624-1</p>
    """,
    "下市校": """
        <p>■下市校住所</p>
        <p>〒638-0041</p>
        <p>奈良県吉野郡下市町下市1818</p>
    """,
    "修正校": """
        <p>■修正校住所</p>
        <p>〒515-0316</p>
        <p>三重県多気郡明和町有爾中816-1</p>
    """,
    "二升石校": """
        <p>■二升石校住所</p>
        <p>〒027-0507<p>
        <p>岩手県下閉伊郡岩泉町二升石字 大根13</p>
    """,
    "生坂校": """
        <p>■生板校</p>
        <p>〒300-1331</p>
        <p>茨城県稲敷郡河内町生板2506</p>
    """,
    "万沢校": """
        <p>■万沢校</p>
        <p>〒409-2103</p>
        <p>山梨県南巨摩郡南部町万沢4119</p>
    """,
    "徳光校": """
        <p>■徳光校</p>
        <p>〒891-0513</p>
        <p>鹿児島県指宿市山川岡児ケ水218-1</p>
    """,
    "海浦校": """
        <p>■海浦校住所</p>
        <p>〒869-5304</p>
        <p>熊本県葦北郡芦北町海浦1315</p>
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
        PLACE.KIKAGAKU: "キカガク",
        PLACE.HIBARI: "ひばりヶ丘校",
        PLACE.KANDA: "神田校",
        PLACE.NAGASAWA: "長沢校",
        PLACE.CHONAN: "長南校",
        PLACE.TANIGUCHI: "谷口校",
        PLACE.ASHIDA: "芦田校",
        PLACE.TADANOUMI: "忠海校",
        PLACE.TOI: "土肥校",
        PLACE.TOMARIKAWA: "泊川校",
        PLACE.SUGATA: "菅田校",
        PLACE.YAMAMORI: "山守校",
        PLACE.KATATA: "片田校",
        PLACE.NAKAMATSU: "中松校",
        PLACE.NAKATSUBARU: "中津原校",
        PLACE.NAGAWAKA: "長若校",
        PLACE.TOMARU: "外丸校",
        PLACE.KAMINOKAE: "上ノ加江校",
        PLACE.SHIMOICHI: "下市校",
        PLACE.SYUSEI: "修正校",
        PLACE.NISYOISHI: "二升石校",
        PLACE.MANAITA: "生板校",
        PLACE.MANZAWA: "万沢校",
        PLACE.TOKKO: "徳光校",
        PLACE.UMINOURA: "海浦校",

        
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
