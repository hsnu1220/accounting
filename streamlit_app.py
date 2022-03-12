import streamlit as st
import pandas as pd
import numpy as np
import requests
import io
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px


### ===== global variables ===== ###
HDR_OUT = '支出'
HDR_TOTAL = '滿月記帳表'
hdr_to_id = dict()
hdr_to_id[HDR_OUT] = 'spending'
hdr_to_id[HDR_TOTAL] = 'accounting'

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

cls_list = [
   cls_rent, cls_life, cls_cook, cls_dine,
   cls_fun, cls_health, cls_move, cls_default
]
hues = px.colors.qualitative.Set3
cls_to_hue = {cls: hue for cls, hue in zip(cls_list, hues)}
col_pct = '比例'


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
   df[col_class] = df[col_tag].transform(tag_to_class)
   return df


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

st.sidebar.markdown(
   f'''
   ## 目錄
   - [{HDR_OUT}](#{hdr_to_id[HDR_OUT]})
   - [{HDR_TOTAL}](#{hdr_to_id[HDR_TOTAL]})
   ''',
   unsafe_allow_html=True
)


### ===== SPENDING ===== ###
st.markdown(
   f'''
   <h1><a id='{hdr_to_id[HDR_OUT]}'>{HDR_OUT}</a></h1>
   ''',
   unsafe_allow_html=True
)
df_raw = get_google_sheet(id=SHEET_ID, name=SHEET_NAME)

# monthly total
st.header('逐月總支出')
df_month = df_raw.groupby(by=col_ym, as_index=False)[col_amount].agg('sum')
fig_month_total = go.Figure(go.Scatter(
   name=col_amount,
   mode='markers',
   x=df_month[col_ym],
   y=df_month[col_amount],
   marker=dict(
      size=16
   )
))
fig_month_total.add_trace(go.Scatter(
   name=f'過去{num_months}個月移動平均',
   mode='lines',
   x=df_month[col_ym],
   y=df_month[col_amount].rolling(num_months, min_periods=1).mean(),
   line=dict(
      width=8
   )
))
st.plotly_chart(fig_month_total)

# recent few months by class
st.header(f'過去{num_months}個月')
ym_list = df_raw[col_ym].dropna().unique().tolist()
fig_recent_class = make_subplots(
   rows=1, cols=num_months,
   specs=[[{'type': 'pie'} for _ in range(num_months)]],
   subplot_titles=ym_list[-num_months:]
)
for idx, ym in enumerate(ym_list[-num_months:]):
   df_month = df_raw[df_raw[col_ym] == ym]
   df_class = df_month.groupby(by=col_class, as_index=False)[col_amount].agg('sum')
   df_class[col_pct] = (
      df_class[col_amount] / df_class[col_amount].sum() * 1E2
   ).transform(lambda pct: f'{pct:.1f}')

   fig_pie = px.pie(
      df_class,
      names=col_class,
      values=col_amount,
      color=col_class,
      color_discrete_map=cls_to_hue,
      hover_data=[col_pct]
   )
   fig_pie.update_traces(
      hovertemplate='%{customdata[0][1]}=%{customdata[0][0]}%<extra></extra>'
   )
   print(fig_pie.data)
   fig_recent_class.add_trace(
      fig_pie.data[0],
      row=1, col=(idx + 1)
   )
fig_recent_class.update_traces(
   textposition='inside',
   textinfo='label+value',
   textfont_size=20,
)
fig_recent_class.update_layout(
   hoverlabel=dict(font_size=16)
)
st.plotly_chart(fig_recent_class)

# monthly detail
st.header('單月類別')
ym = st.selectbox(label='年/月', options=ym_list, index=len(ym_list)-1)
df_month = df_raw[df_raw[col_ym] == ym]
df_class = df_month.groupby(by=col_class)[col_amount].agg('sum')
st.table(df_class.sort_values(ascending=False))
with st.expander('明細'):
   st.table(df_month.drop(columns=[col_class]))

# every month by class
st.header('逐月類別')
fig_month_class = px.bar(
   data_frame=df_raw,
   x=col_ym,
   y=col_amount,
   color=col_class,
   color_discrete_map=cls_to_hue
)
st.plotly_chart(fig_month_class)


### ===== MONTHLY ACCOUNTING ===== ###
st.markdown(
   f'''
   <h1><a id='{hdr_to_id[HDR_TOTAL]}'>{HDR_TOTAL}</a></h1>
   ''',
   unsafe_allow_html=True
)
st.write('WIP')
