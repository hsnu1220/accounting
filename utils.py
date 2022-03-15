import requests
import io
import pandas as pd
import consts as C


def tag_to_class(tag):
   if tag in ['蹛', '水電', '厝內']:
      return C.CLS_RENT
   elif tag in ['家具', '度日', '植物', '穿插', '梳妝']:
      return C.CLS_LIFE
   elif tag in ['菜市', '超市', '做麭']:
      return C.CLS_COOK
   elif tag in ['好料', '四秀', '食涼']:
      return C.CLS_DINE
   elif tag in ['冊', '票', '麻雀', '網影', '順紲']:
      return C.CLS_FUN
   elif tag in ['保健', '運動']:
      return C.CLS_HEALTH
   elif tag in ['駛車', '騎車', '通勤', '坐車']:
      return C.CLS_MOVE
   else:
      return C.CLS_DEFAULT


# @st.cache(suppress_st_warning=True)
def get_google_sheet(id, name):
   end_point = 'https://docs.google.com/spreadsheets/d'
   url = f'{end_point}/{id}/gviz/tq?tqx=out:csv&sheet={name}'
   content = requests.get(url).content

   df = pd.read_csv(
      io.StringIO(content.decode('utf-8')),
      usecols=C.COLS_GOOGLE_SHEET
   ).fillna(value='')
   df[C.COL_AMOUNT] = df[C.COL_AMOUNT].astype('int32')
   df[C.COL_PAY] = df[C.COL_PAY].replace('', C.PAY_DEFAULT)
   df[C.COL_FREQ] = df[C.COL_FREQ].replace('', C.FREQ_DEFAULT)
   df[C.COL_CLASS] = df[C.COL_TAG].transform(tag_to_class)

   return df
