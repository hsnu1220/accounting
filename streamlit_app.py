import streamlit as st
import pandas as pd
import requests
import io
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px


### ===== global variables ===== ###
HDR_OUT = '支出'
HDR_NET = '滿月記帳表'
HDR_DOC = '說明'
hdr_to_id = dict()
hdr_to_id[HDR_OUT] = 'spending'
hdr_to_id[HDR_NET] = 'accounting'
hdr_to_id[HDR_DOC] = 'documentation'

# SHEET_ID = '1WgZrSv9pNPyAd7IutFJ43aB5UX8KiWGGSEfHK76xoS4'
SHEET_ID = '1-wag8UYLCjzHL-kzvc81TwAOunPTVK01Cq3ZsO5ukck'
SHEET_NAME = '總表'

col_ym = '年月'
col_dd = '日'
col_store = '店'
col_item = '項'
col_amount = '額'
col_tag = '標'
col_pay = '方式'
col_freq = '頻率'
cols_sheet = [
   col_ym, col_dd, col_store, col_item, col_amount,
   col_tag, col_pay, col_freq
]

col_class = '類'
cls_rent = '租'
cls_life = '生活'
cls_cook = '煮食'
cls_dine = '食外'
cls_fun = '消遣'
cls_health = '健康'
cls_move = '交通'
cls_default = '無'
classes = [
   cls_rent, cls_life, cls_cook, cls_dine,
   cls_fun, cls_health, cls_move, cls_default
]

pay_card = '卡'
pay_digit = '數碼'
pay_default = '現金'
pays = [pay_card, pay_digit, pay_default]

freq_month = '每月'
freq_bimonth = '隔月'
freq_trip = '𨑨迌'
freq_year = '過年'
freq_topup = '入錢'
freq_sub = '訂閱'
freq_default = '一擺'
freqs = [
   freq_month, freq_bimonth, freq_trip, freq_year,
   freq_topup, freq_sub, freq_default
]

col_pct = '比例'
hues = px.colors.qualitative.Set3
FONT_SIZE_TEXT = 20
FONT_SIZE_HOVER = 16


### ===== helper functions ===== ###
def tag_to_class(tag):
   if tag in ['蹛', '水電', '厝內']:
      return cls_rent
   elif tag in ['家具', '度日', '植物', '穿插', '梳妝']:
      return cls_life
   elif tag in ['菜市', '超市', '做麭']:
      return cls_cook
   elif tag in ['好料', '四秀', '食涼']:
      return cls_dine
   elif tag in ['冊', '票', '麻雀', '網影', '順紲']:
      return cls_fun
   elif tag in ['保健', '運動']:
      return cls_health
   elif tag in ['駛車', '騎車', '通勤', '坐車']:
      return cls_move
   else:
      return cls_default


# @st.cache(suppress_st_warning=True)
def get_google_sheet(id, name):
   end_point = 'https://docs.google.com/spreadsheets/d'
   url = f'{end_point}/{id}/gviz/tq?tqx=out:csv&sheet={name}'
   content = requests.get(url).content

   df = pd.read_csv(
      io.StringIO(content.decode('utf-8')),
      usecols=cols_sheet
   ).fillna(value='')
   df[col_amount] = df[col_amount].astype('int32')
   df[col_pay] = df[col_pay].replace('', pay_default)
   df[col_freq] = df[col_freq].replace('', freq_default)
   df[col_class] = df[col_tag].transform(tag_to_class)

   return df


def get_color_map(group=col_class):
   arr = classes
   if group == col_pay:
      arr = pays
   elif group == col_freq:
      arr = freqs
   return {elm: hue for elm, hue in zip(arr, hues)}


### ===== page config ===== ###
st.set_page_config(
   page_title='布基帳',
   page_icon=':whale:',
   layout='centered',
   initial_sidebar_state='collapsed'
)


### ===== sidebar ===== ###
st.sidebar.header('比較範圍')
num_months = int(st.sidebar.text_input(label='月', value='3'))
st.sidebar.header('分組')
col_group = st.sidebar.radio(
   label='照',
   options=[col_class, col_pay, col_freq],
)

st.sidebar.markdown(
   f"""
   ## 目錄
   - [{HDR_NET}](#{hdr_to_id[HDR_NET]})
   - [{HDR_OUT}](#{hdr_to_id[HDR_OUT]})
   - [{HDR_DOC}](#{hdr_to_id[HDR_DOC]})
   """,
   unsafe_allow_html=True
)


### ===== MONTHLY ACCOUNTING ===== ###
st.markdown(
   f'''
   <h1><a id='{hdr_to_id[HDR_NET]}'>{HDR_NET}</a></h1>
   ''',
   unsafe_allow_html=True
)
st.write('WIP')


### ===== SPENDING ===== ###
st.markdown(
   f'''
   <h1><a id='{hdr_to_id[HDR_OUT]}'>{HDR_OUT}</a></h1>
   ''',
   unsafe_allow_html=True
)
df_raw = get_google_sheet(id=SHEET_ID, name=SHEET_NAME)
ym_list = df_raw[col_ym].dropna().unique().tolist()

# monthly total
st.header('攏總')
df_total = df_raw.groupby(by=col_ym, as_index=False)[col_amount].agg('sum')
fig_total = go.Figure(go.Scatter(
   name=col_amount,
   mode='markers',
   x=df_total[col_ym],
   y=df_total[col_amount],
   marker=dict(
      size=16
   )
))
fig_total.add_trace(go.Scatter(
   name=f'過去{num_months}個月移動平均',
   mode='lines',
   x=df_total[col_ym],
   y=df_total[col_amount].rolling(num_months, min_periods=1).mean(),
   line=dict(
      width=8
   )
))
st.plotly_chart(fig_total)

# recent few months by class
st.header(f'過去{num_months}個月')
fig_recent = make_subplots(
   rows=1, cols=num_months,
   specs=[[{'type': 'pie'} for _ in range(num_months)]],
   subplot_titles=[
      f'{ym}<br>${total}'
      for ym, total in zip(df_total[col_ym], df_total[col_amount])
   ][-num_months:]
)
for idx, ym in enumerate(ym_list[-num_months:]):
   df_month = df_raw.query(f'{col_ym} == @ym')
   df_class = df_month.groupby(by=col_group, as_index=False)[col_amount].agg('sum')
   df_class[col_pct] = (
      df_class[col_amount] / df_class[col_amount].sum() * 1E2
   ).transform(lambda pct: f'{pct:.1f}')

   fig_pie = px.pie(
      df_class,
      names=col_group,
      values=col_amount,
      color=col_group,
      color_discrete_map=get_color_map(col_group),
      hover_data=[col_pct]
   )
   fig_pie.update_traces(
      hovertemplate='%{customdata[0][1]}=%{customdata[0][0]}%<extra></extra>'
   )
   fig_recent.add_trace(
      fig_pie.data[0],
      row=1, col=(idx + 1)
   )
fig_recent.update_traces(
   textposition='inside',
   textinfo='label+value',
   textfont_size=FONT_SIZE_TEXT,
)
fig_recent.update_layout(
   hoverlabel=dict(font_size=FONT_SIZE_HOVER)
)
st.plotly_chart(fig_recent)

# monthly detail
st.header('這月分組')
ym = st.selectbox(label=col_ym, options=ym_list, index=len(ym_list)-1)
df_month = df_raw.query(f'{col_ym} == @ym')
df_class = df_month.groupby(by=col_group, as_index=False)[col_amount].agg('sum')
df_class.sort_values(by=col_amount, inplace=True)
num_classes = df_class[col_group].shape[0]
fig_month = make_subplots(
   rows=1, cols=num_classes,
   specs=[[{'type': 'pie'} for _ in range(num_classes)]],
   subplot_titles=[
      f'{cls}<br>${total}'
      for cls, total in zip(df_class[col_group], df_class[col_amount])
   ]
)
for idx, cls in enumerate(df_class[col_group]):
   df_class = df_month.query(f'{col_group} == @cls')
   df_tag = df_class.groupby(by=col_tag, as_index=False)[col_amount].agg('sum')
   fig_month.add_trace(
      go.Pie(
         labels=df_tag[col_tag],
         values=df_tag[col_amount],
         textposition='inside',
         textinfo='label+value',
         textfont_size=FONT_SIZE_TEXT,
         hoverinfo='label+percent',
         marker=dict(colors=hues),
         showlegend=False
      ),
      row=1, col=(idx + 1)
   )
fig_month.update_layout(
   hoverlabel=dict(font_size=FONT_SIZE_HOVER)
)
st.plotly_chart(fig_month)
with st.expander('明細'):
   st.table(df_month.drop(columns=[col_ym, col_pay, col_freq]))

# each month by class
st.header('逐月分組')
fig_all = px.bar(
   data_frame=df_raw,
   x=col_ym,
   y=col_amount,
   color=col_group,
   color_discrete_map=get_color_map(col_group)
)
st.plotly_chart(fig_all)


### ===== DOCUMENTATION ===== ###
st.markdown(
   f'''
   <h1><a id='{hdr_to_id[HDR_DOC]}'>{HDR_DOC}</a></h1>
   ''',
   unsafe_allow_html=True
)
st.markdown(
   """
   ### 標
   - 租：月租
      - 蹛：(出遊)住宿、管理費
      - 水電：水、電、瓦斯、電信(網路)
      - 厝內：孝親費、紅包、幫家裡代買
   - 生活
      - 家具：非消耗品
      - 度日：消耗品
      - 植物
      - 穿插：含鞋子
      - 梳妝：保養品、剪髮
   - 煮食
      - 菜市：菜市場、水果行
      - 超市：大潤發、全聯、希望廣場
      - 做麭：做麵包食材
   - 食外：外食
      - 好料：外食錢包
      - 四秀：零食
      - 食涼：飲料
   - 消遣：娛樂
      - 冊
      - 票：電影票、表演門票、球賽門票
      - 網影：串流平台(為訂閱)
      - 麻雀：打麻將
      - 順紲：幫朋友代買
   - 健康
      - 保健：保健食品、看醫生
      - 運動：含裝備、場地費
   - 交通：加油、停車費跟所用之交通工具
      - 駛車：汽車
      - 騎車：機車
      - 通勤：捷運、UBike(抓關鍵字「悠遊卡儲值」)
      - 坐車：計程車、(出遊之)火車、高鐵、飛機

   ### 方式
   - 卡：信用卡
   - 數碼：數位支付如街口、悠遊付
   - (空白)：預設為現金

   ### 頻率
   - 每月
   - 隔月
   - 𨑨迌：出遊
   - 過年：紅包
   - 入錢：可寫在項目即可，會自動抓關鍵字「儲值」、「加值」
   - 訂閱
   - (空白)：預設為一擺

   ### FAQ
   - 保險：算訂閱、類別跟保險項目
   """,
   unsafe_allow_html=True
)
