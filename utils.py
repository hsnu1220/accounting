import io
import requests
import pandas as pd
from plotly import express as px
import consts as C


# =============== #
# Private helpers #
# =============== #
def load_df_from_url(url, cols):
   content = requests.get(url).content
   df = pd.DataFrame()
   df = pd.read_csv(
      io.StringIO(content.decode('utf-8')),
      usecols=cols
   ).fillna(value='')
   return df


def rm_substr(s, kw, to_char=''):
   return s.replace(kw, to_char)


def rm_comma(s):
   return rm_substr(s, ',')


def rm_float(s):
   return rm_substr(s, '.00')


def is_credit_bill(s):
   return any(kw in s for kw in ['花旗銀行信用卡', '阿魚', '台新', '國泰', '渣打'])


# ============== #
# Public helpers #
# ============== #
def trim_store(s):
   for kw_sym in ('－', '０', '/', '＊', '＆'):
      s = rm_substr(s, kw_sym)
   for kw_loc in (
      '台灣',
      'TW',
      'TAIPEI',
      'Taipei',
      'CITY',
      'City',
      'HSINCHU',
      'YUANLIN',
      'YUNLIN',
      'TAICHUNG',
      'KAOHSIUNG',
      'PINGTUNG',
      'Pingtung',
      'TAITUNG',
      'HUALIEN'
   ):
      s = rm_substr(s, kw_loc)
   for kw_store in (
      '股份有限',
      '時尚廣場',
      '財團法人',
      '便利商',
      '實業',
      '公司',
      '餐廳',
      '生活',
      '百貨',
      '超商',
      '藥妝',
      '門巿'
   ):
      s = rm_substr(s, kw_store)
   for kw_else in (
      'Ｕｎｏｃｈ',
      'ＭＯＳ',
      '（Ｄ２',
      '＆ｂ',
      '不抵用五倍券',
      '網路／語',
      '電支'
   ):
      s = rm_substr(s, kw_else)
   return s.strip()


# ======= #
# Mapping #
# ======= #
def store_to_tag(s):
   if any(kw in s for kw in ['瓦斯', '中華電信', '台哥大']):
      return C.TAG_BILL
   elif any(kw in s for kw in ['必勝客']):
      return C.TAG_FAMILY
   elif any(kw in s for kw in ['宜家家居', '宜得利']):
      return C.TAG_FURNISH
   elif any(kw in s for kw in ['日藥本舖', '康是美', '金興發', '大創', '寶雅']):
      return C.TAG_CONSUMABLE
   elif any(kw in s for kw in ['健康食彩', '大潤發', '家樂福', '全聯', '黑沃']):
      return C.TAG_MARKET
   elif any(kw in s for kw in [
      'ＦｏｏｄＰａｎｄａ',
      'ｆｏｏｄｐａｎｄａ',
      '誠品信義店',
      '川川川川',
      '春秋大滷',
      '好想見麵',
      '麥味登',
      '龍涎居',
      '麥當勞',
      '休息站',
      '優食',
      '早點',
      '胡饕',
      '摩斯',
      '統一',
      '誠記',
      '全家',
      '素食',
      'ＯＫ'
   ]):
      return C.TAG_FORAGE
   elif any(kw in s for kw in [
      '約翰紅茶',
      '萊爾富',
      '茶湯會',
      '康青龍',
      '星巴克',
      '醋頭家',
      '清心',
      '烏弄',
      '山焙',
      '５嵐'
   ]):
      return C.TAG_DRINK
   elif any(kw in s for kw in [
      '國家表演藝術中心',
      '臺北表演藝術中心',
      '融藝',
      'ｕｄｎ售票',
      'ＫＫＴＩＸ',
      '威秀',
      '秀泰'
   ]):
      return C.TAG_SHOW
   elif any(kw in s for kw in ['ＤＥＣＡＴＨＬＯＮ', '迪卡儂', '捷安特']):
      return C.TAG_EXERCISE
   elif any(kw in s for kw in ['微笑單車', '悠遊付', '悠遊卡', 'Ｇｏ Ｓｈａｒｅ']):
      return C.TAG_COMMUTE
   elif any(kw in s for kw in ['計程車', '大都會衛星']):
      return C.TAG_TAXI
   else:
      return C.TAG_DEFAULT


def tag_to_class(tag):
   if tag in C.TAGS_RENT:
      return C.CLS_RENT
   elif tag in C.TAGS_LIFE:
      return C.CLS_LIFE
   elif tag in C.TAGS_COOK:
      return C.CLS_COOK
   elif tag in C.TAGS_DINE:
      return C.CLS_DINE
   elif tag in C.TAGS_FUN:
      return C.CLS_FUN
   elif tag in C.TAGS_HEALTH:
      return C.CLS_HEALTH
   elif tag in C.TAGS_MOVE:
      return C.CLS_MOVE
   else:
      return C.CLS_DEFAULT


# ==== #
# Cash #
# ==== #
# @st.cache(suppress_st_warning=True)
def get_df_cash(sheet_id, tables=C.YY_LIST):
   df = pd.DataFrame()
   for yy in tables:
      df_year = load_df_from_url(
         f'{C.END_POINT}/{sheet_id}/gviz/tq?tqx=out:csv&sheet={yy}',
         C.COLS_SHEET_CASH
      )
      df_year[C.COL_MM] = df_year[C.COL_MM].transform(
         lambda mm: f'{yy}/{mm:02d}'
      )
      df = df.append(df_year, ignore_index=True)

   df[C.COL_PAY] = df[C.COL_PAY].replace('', C.PAY_CASH)
   return df


# ==== #
# Bank #
# ==== #
def get_df_ctbc(sheet_id, tables=C.YY_LIST):
   df = pd.DataFrame()
   for yy in tables:
      df_year = load_df_from_url(
         f'{C.END_POINT}/{sheet_id}/gviz/tq?tqx=out:csv&sheet={yy}',
         C.COLS_SHEET_CTBC,
      )
      df = df.append(df_year, ignore_index=True)

   df[C.COL_MM] = df[C.COL_DATE].transform(
      lambda s: '/'.join(s.split('/')[:-1])
   )
   df[C.COL_DD] = df[C.COL_DATE].str.split('/').transform(
      lambda arr: arr[-1]
   )
   df.drop(columns=[C.COL_DATE], inplace=True)
   for col in (C.COL_AMOUNT, C.COL_DEPOSIT):
      df[col] = df[col].transform(rm_comma)

   return df


def parse_spending_from_ctbc(df):
   df.drop(columns=[C.COL_DEPOSIT], inplace=True)
   df = df[df[C.COL_AMOUNT] != '']
   df = df[df[C.COL_STORE] != 'ＡＴＭ']

   df = df[~df[C.COL_ITEM].transform(is_credit_bill)]
   for kw, tag in zip(['孝親', '房租'], [C.TAG_FAMILY, C.TAG_SLEEP]):
      df.loc[
         df[C.COL_ITEM].str.contains(kw),
         [C.COL_TAG, C.COL_FREQ]
      ] = tag, C.FREQ_MONTH
   df[C.COL_PAY] = df[C.COL_PAY].replace('', C.PAY_DIGIT)

   return df


# =========== #
# Credit card #
# =========== #
def get_df_citi(sheet_id, tables=C.YY_LIST):
   df = pd.DataFrame()
   for yy in tables:
      df_year = load_df_from_url(
         f'{C.END_POINT}/{sheet_id}/gviz/tq?tqx=out:csv&sheet={yy}',
         C.COLS_SHEET_CITI,
      )
      df = df.append(df_year, ignore_index=True)

   df[C.COL_MM] = df[C.COL_DATE].transform(
      lambda s: '/'.join(s.split('/')[::-1][:-1])
   )
   df[C.COL_DD] = df[C.COL_DATE].str.split('/').transform(
      lambda arr: arr[0]
   )
   df.drop(columns=[C.COL_DATE], inplace=True)
   df = df[~df[C.COL_AMOUNT].str.startswith('-')]
   df[C.COL_AMOUNT] = df[C.COL_AMOUNT].transform(rm_float).transform(rm_comma)
   # 連加：Line Pay
   for kw in ('街口', '連加'):
      df.loc[df[C.COL_STORE].str.contains(kw), C.COL_PAY] = C.PAY_DIGIT
   df[C.COL_PAY] = df[C.COL_PAY].replace('', C.PAY_CARD)

   return df


def get_df_tsib(sheet_id, tables=C.YY_LIST):
   df = pd.DataFrame()
   for yy in tables:
      df_year = load_df_from_url(
         f'{C.END_POINT}/{sheet_id}/gviz/tq?tqx=out:csv&sheet={yy}',
         C.COLS_SHEET_TSIB,
      )
      df = df.append(df_year, ignore_index=True)

   df[[C.COL_YY, C.COL_MM, C.COL_DD]] = df[C.COL_DATE].str.split(
      '/',
      expand=True
   )
   df[C.COL_MM] = df[C.COL_MM].transform(lambda mm: f'{mm:0>2}')
   df[C.COL_MM] = df[C.COL_YY] + '/' + df[C.COL_MM]
   df.drop(columns=[C.COL_DATE, C.COL_YY], inplace=True)
   # 連加：Line Pay
   for kw in ('街口', '連加'):
      df.loc[df[C.COL_STORE].str.contains(kw), C.COL_PAY] = C.PAY_DIGIT
   df[C.COL_PAY] = df[C.COL_PAY].replace('', C.PAY_CARD)

   return df



########
# Plot #
########
def get_color_map(group=C.COL_CLASS):
   arr = C.CLASSES
   if group == C.COL_PAY:
      arr = C.PAYS
   elif group == C.COL_FREQ:
      arr = C.FREQS
   map_hue = {
      elm: hue for elm, hue in zip(arr, px.colors.qualitative.Set3)
   }
   return map_hue