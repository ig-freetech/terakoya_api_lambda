from enum import Enum


class TERAKOYA_TYPE(Enum):
    """テラコヤ種別 (terakoya_type)"""
    HIGH_IKE = 1
    """カフェ塾テラコヤ(池袋)"""
    ONLINE_TAMA = 2
    """オンラインテラコヤ(多摩)"""
    MID_IKE = 3
    """テラコヤ中等部(池袋)"""
    MID_SHIBU = 4
    """テラコヤ中等部(渋谷)"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class ARRIVAL_TIME(Enum):
    """到着予定時間帯 (arrival_time)"""
    BEFORE_1700 = 1
    """17:00前"""
    FROM_1700_TO_1730 = 2
    """17:00~17:30"""
    FROM_1730_TO_1800 = 3
    """17:30~18:00"""
    AFTER_1800 = 4
    """18:00以降"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class GRADE(Enum):
    """学年 (grade)"""
    HIGH_1 = 1
    """高校1年生"""
    HIGH_2 = 2
    """高校2年生"""
    HIGH_3 = 3
    """高校3年生"""
    MID_1 = 11
    """中学1年生"""
    MID_2 = 12
    """中学2年生"""
    MID_3 = 13
    """中学3年生"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class TERAKOYA_EXPERIENCE(Enum):
    """テラコヤ参加経験 (terakoya_experience)"""
    FIRST_TIME = 1
    """今回が初回"""
    DONE = 2
    """過去に参加したことがある"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class STUDY_SUBJECT(Enum):
    """勉強したい科目 (study_subject)"""
    ENG = 1
    """英語"""
    JPN = 2
    """国語"""
    MAT = 3
    """数学"""
    SOC = 4
    """社会"""
    SCI = 5
    """理科"""
    AO_ENTRANCE = 6
    """推薦型入試対策（志望理由書・面接など）"""
    ORIENTATION = 7
    """大学説明会"""
    CAREER = 8
    """キャリア説明会"""
    EIKEN = 9
    """英検"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class STUDY_STYLE(Enum):
    """勉強スタイル (study_style)"""
    SILENT = 1
    """黙々と静かに勉強したい"""
    QUESTION = 2
    """分からない点があったらスタッフに質問したい"""
    TALKING = 3
    """友達と話しながら楽しく勉強したい"""
    WITH = 4
    """1人では難しいのでスタッフ付きっ切りで勉強を教えて欲しい"""
    CONSULT = 5
    """勉強も教えて欲しいけどスタッフの話を聞いたり、相談したい。"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class COURSE_CHOICE(Enum):
    """文理選択 (course_choice)"""
    TBD = 1
    """まだ決めていない"""
    LIBERAL_ARTS = 2
    """文系"""
    SCIENCE = 3
    """理系"""
    NULL = 999
    """NULL"""


class HOW_TO_KNOW_TERAKOYA(Enum):
    """テラコヤを知ったきっかけ (how_to_know_terakoya)"""
    HP = 1
    """HP"""
    INSTAGRAM = 2
    """Instagram"""
    FACEBOOK = 3
    """Facebook"""
    TWITTER = 4
    """Twitter"""
    INTRODUCE = 5
    """知人の紹介"""
    OTHER = 0
    """その他"""
    NULL = 999
    """NULL"""


class PLACE(Enum):
    """拠点 (Place)"""
    TBD = 0
    """未設定"""
    SUNSHINE = 1
    """サンシャインシティ"""
    RYOHIN = 2
    """良品計画本社"""
    DIORAMA_CAFE = 3
    """DIORAMA CAFE"""
    CAREER_MOM = 4
    """キャリア・マム"""
    KIKAGAKU = 5
    """キカガク"""
    NULL = 999
    """NULL"""
