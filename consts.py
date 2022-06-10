# ============= #
# Streamlit app #
# ============= #
PAGE_TITLE = '布基帳'
PAGE_ICON = ':whale:'


# ============ #
# Google sheet #
# ============ #
END_POINT = 'https://docs.google.com/spreadsheets/d'
SHEET_ID_BANK_CTBC = '1OqB6azVpGt6ebkDyKboPyk2-Gy45jn9Ht5nupG7bOTc'
YY_LIST = ['2021', '2022']


# ======== #
# Spending #
# ======== #
COL_MM = '月'
COL_DD = '日'
COL_STORE = '店'
COL_ITEM = '項'
COL_AMOUNT = '額'
COL_TAG = '標'
COL_FREQ = '頻率'
COL_PAY = '方式'

COLS_SPENDING = [COL_TAG, COL_FREQ, COL_PAY]


# ==== #
# Cash #
# ==== #
COLS_SHEET_CASH = [
   COL_MM, COL_DD, COL_STORE, COL_ITEM, COL_AMOUNT
] + COLS_SPENDING


# ==== #
# Bank #
# ==== #
COL_DATE_CTBC = '日期'
COL_DEPOSIT = '存入'

COLS_SHEET_CTBC = [
   COL_DATE_CTBC, COL_AMOUNT, COL_DEPOSIT, COL_STORE, COL_ITEM,
] + COLS_SPENDING


# =========== #
# Credit card #
# =========== #
COL_DATE_CITI = '交易日期'

COLS_SHEET_CITI = [
   COL_DATE_CITI, COL_STORE, COL_AMOUNT, COL_ITEM
] + COLS_SPENDING


# ============ #
# Tag to label #
# ============ #
TAG_SLEEP = '蹛'
TAG_BILL = '水電'
TAG_FAMILY = '厝內'
TAGS_RENT = [TAG_SLEEP, TAG_BILL, TAG_FAMILY]

TAG_FURNISH = '家具'
TAG_CONSUMABLE = '度日'
TAG_FLORA = '植物'
TAG_WEARING = '穿插'
TAG_DRESS = '梳妝'
TAGS_LIFE = [
   TAG_FURNISH, TAG_CONSUMABLE,
   TAG_FLORA, TAG_WEARING, TAG_DRESS
]

TAG_FARMER = '菜市'
TAG_MARKET = '超市'
TAG_BAKE = '做麭'
TAGS_COOK = [TAG_FARMER, TAG_MARKET, TAG_BAKE]

TAG_FORAGE = '好料'
TAG_SNACK = '四秀'
TAG_DRINK = '食涼'
TAGS_DINE = [TAG_FORAGE, TAG_SNACK, TAG_DRINK]

TAG_BOOK = '冊'
TAG_SHOW = '票'
TAG_GAME = '麻雀'
TAG_STREAM = '網影'
TAG_FRIEND = '順紲'
TAGS_FUN = [TAG_BOOK, TAG_SHOW, TAG_GAME, TAG_STREAM, TAG_FRIEND]

TAG_PILL = '保健'
TAG_EXERCISE = '運動'
TAGS_HEALTH = [TAG_PILL, TAG_EXERCISE]

TAG_CAR = '駛車'
TAG_SCOOTER = '騎車'
TAG_COMMUTE = '通勤'
TAG_TAXI = '坐車'
TAGS_MOVE = [TAG_CAR, TAG_SCOOTER, TAG_COMMUTE, TAG_TAXI]

TAG_DEFAULT = f'無{COL_TAG}'


# =============== #
# Derived classes #
# =============== #
COL_CLASS = '類'
COLS_TYPE = [COL_CLASS, COL_PAY, COL_FREQ]

CLS_RENT = '租'
CLS_LIFE = '生活'
CLS_COOK = '煮食'
CLS_DINE = '食外'
CLS_FUN = '消遣'
CLS_HEALTH = '健康'
CLS_MOVE = '交通'
CLS_DEFAULT = f'無{COL_CLASS}'

CLASSES = [
   CLS_RENT, CLS_LIFE, CLS_COOK, CLS_DINE,
   CLS_FUN, CLS_HEALTH, CLS_MOVE, CLS_DEFAULT
]


# ==================== #
# Spending frequencies #
# ==================== #
FREQ_MONTH = '每月'
FREQ_BIMONTH = '隔月'
FREQ_TRIP = '𨑨迌'
FREQ_YEAR = '過年'
FREQ_TOPUP = '入錢'
FREQ_SUB = '訂閱'
FREQ_ONCE = '一擺'

FREQS = [
   FREQ_MONTH, FREQ_BIMONTH, FREQ_TRIP, FREQ_YEAR,
   FREQ_TOPUP, FREQ_SUB, FREQ_ONCE
]


# =============== #
# Payment methods #
# =============== #
PAY_DIGIT = '數碼'
PAY_CARD = '卡'
PAY_CASH = '現金'

PAYS = [PAY_CARD, PAY_DIGIT, PAY_CASH]
