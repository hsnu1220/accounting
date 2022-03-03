import streamlit as st
import pandas as pd
import requests
import io
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px


### ===== global variables ===== ###
hdr_out = '支出'
hdr_total = '滿月記帳表'
map_hdr_id = dict()
map_hdr_id[hdr_out] = 'spending'
map_hdr_id[hdr_total] = 'accounting'

ym_format = '%Y/%m'
date_format = f'{ym_format}/%d'
col_ym = '年/月'

col_date = '日期'
col_store = '商店'
col_item = '項目'
col_amount = '金額'
col_class = '類別'
cols_sheet = [col_date, col_store, col_item, col_amount, col_class]

hues = px.colors.qualitative.Safe


### ===== helper functions ===== ###
# @st.cache(suppress_st_warning=True)
def get_google_sheet(serial_num, name):
   end_point = 'https://docs.google.com/spreadsheets/d'
   url = f'{end_point}/{serial_num}/gviz/tq?tqx=out:csv&sheet={name}'
   content = requests.get(url).content

   df = pd.read_csv(
      io.StringIO(content.decode('utf-8')),
      index_col=0,
      parse_dates=True,
      usecols=cols_sheet
   ).fillna(value='')

   df[col_amount] = df[col_amount].str.replace(r'[\$,]', '', regex=True).astype('int32')
   df[col_ym] = df.index.strftime(ym_format)
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
   - [{hdr_out}](#{map_hdr_id[hdr_out]})
   - [{hdr_total}](#{map_hdr_id[hdr_total]})
   ''',
   unsafe_allow_html=True
)


### ===== spending ===== ###
st.markdown(
   f'''
   <h1><a id='{map_hdr_id[hdr_out]}'>{hdr_out}</a></h1>
   ''',
   unsafe_allow_html=True
)
df_raw = get_google_sheet(
   serial_num='1WgZrSv9pNPyAd7IutFJ43aB5UX8KiWGGSEfHK76xoS4',
   name='總表'
)

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

   fig_recent_class.add_trace(
      go.Pie(
         labels=df_class[col_class],
         values=df_class[col_amount],
         hoverinfo='label+percent',
         textposition='inside',
         textinfo='label+value',
         textfont_size=20,
         marker=dict(colors=hues),
         showlegend=False
      ),
      row=1, col=(idx + 1)
   )
st.plotly_chart(fig_recent_class)

# monthly detail
st.header('單月類別')
ym = st.selectbox(label='年/月', options=ym_list, index=len(ym_list)-1)
df_month = df_raw[df_raw[col_ym] == ym]
df_class = df_month.groupby(by=col_class)[col_amount].agg('sum')
st.table(df_class.sort_values(ascending=False))
with st.expander('明細'):
   df_month.index = df_month.index.strftime(date_format)
   st.table(df_month.drop(columns=[col_ym]))

# every month by class
st.header('逐月類別')
fig_month_class = px.bar(
   data_frame=df_raw,
   x=col_ym,
   y=col_amount,
   color=col_class,
   color_discrete_sequence=hues
)
st.plotly_chart(fig_month_class)


### ===== monthly accounting ===== ###
st.markdown(
   f'''
   <h1><a id='{map_hdr_id[hdr_total]}'>{hdr_total}</a></h1>
   ''',
   unsafe_allow_html=True
)
st.write('WIP')
