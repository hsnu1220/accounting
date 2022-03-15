### ===== google sheet columns ===== ###
COL_YM = '年月'
COL_DD = '日'
COL_STORE = '店'
COL_ITEM = '項'
COL_AMOUNT = '額'
COL_TAG = '標'
COL_PAY = '方式'
COL_FREQ = '頻率'
COLS_GOOGLE_SHEET = [
   COL_YM, COL_DD, COL_STORE, COL_ITEM, COL_AMOUNT,
   COL_TAG, COL_PAY, COL_FREQ
]


### ===== derived classes ===== ###
COL_CLASS = '類'
CLS_RENT = '租'
CLS_LIFE = '生活'
CLS_COOK = '煮食'
CLS_DINE = '食外'
CLS_FUN = '消遣'
CLS_HEALTH = '健康'
CLS_MOVE = '交通'
CLS_DEFAULT = '無'
CLASSES = [
   CLS_RENT, CLS_LIFE, CLS_COOK, CLS_DINE,
   CLS_FUN, CLS_HEALTH, CLS_MOVE, CLS_DEFAULT
]


### ===== payment methods ===== ###
PAY_CARD = '卡'
PAY_DIGIT = '數碼'
PAY_DEFAULT = '現金'
PAYS = [PAY_CARD, PAY_DIGIT, PAY_DEFAULT]


### ===== spending frequency ===== ###
FREQ_MONTH = '每月'
FREQ_BIMONTH = '隔月'
FREQ_TRIP = '𨑨迌'
FREQ_YEAR = '過年'
FREQ_TOPUP = '入錢'
FREQ_SUB = '訂閱'
FREQ_DEFAULT = '一擺'
FREQS = [
   FREQ_MONTH, FREQ_BIMONTH, FREQ_TRIP, FREQ_YEAR,
   FREQ_TOPUP, FREQ_SUB, FREQ_DEFAULT
]
