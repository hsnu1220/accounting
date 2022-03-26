import streamlit as st
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px
import consts as C
from utils import get_google_sheet
import math


### ===== Global variables ===== ###
HDR_OUT = '支出'
HDR_NET = '滿月記帳表'
HDR_DOC = '說明'

hdr_to_id = dict()
hdr_to_id[HDR_OUT] = 'spending'
hdr_to_id[HDR_NET] = 'accounting'
hdr_to_id[HDR_DOC] = 'documentation'

SHEET_ID = '1-wag8UYLCjzHL-kzvc81TwAOunPTVK01Cq3ZsO5ukck'
SHEET_NAME = '總表'

COL_PCT = '比例'
HUES = px.colors.qualitative.Set3
FONT_SIZE_TICK = 16
FONT_SIZE_TEXT = 20
FONT_SIZE_HOVER = 16


### ===== Helper functions ===== ###
def get_color_map(group=C.COL_CLASS):
   arr = C.CLASSES
   if group == C.COL_PAY:
      arr = C.PAYS
   elif group == C.COL_FREQ:
      arr = C.FREQS
   return {elm: hue for elm, hue in zip(arr, HUES)}


### ===== Page config ===== ###
st.set_page_config(
   page_title='布基帳',
   page_icon=':whale:',
   layout='centered',
   initial_sidebar_state='collapsed'
)


### ===== Sidebar ===== ###
st.sidebar.markdown(
   f"""
   ## 目錄
   - [{HDR_NET}](#{hdr_to_id[HDR_NET]})
   - [{HDR_OUT}](#{hdr_to_id[HDR_OUT]})
   - [{HDR_DOC}](#{hdr_to_id[HDR_DOC]})
   """,
   unsafe_allow_html=True
)
st.sidebar.header('分組')
col_group = st.sidebar.radio(
   label='照',
   options=[C.COL_CLASS, C.COL_PAY, C.COL_FREQ],
)
st.sidebar.header('比較範圍')
radius_months = int(st.sidebar.text_input(label='頭尾幾個月', value='1'))
num_months_focus = radius_months * 2 + 1


### ===== Monthly accounting ===== ###
st.header(HDR_NET, anchor=hdr_to_id[HDR_NET])
st.write('WIP')


### ===== Spending ===== ###
st.header(HDR_OUT, anchor=hdr_to_id[HDR_OUT])
df_raw = get_google_sheet(id=SHEET_ID, name=SHEET_NAME)
ym_list = df_raw[C.COL_YM].dropna().unique().tolist()
num_months_total = len(ym_list)


# monthly total
st.markdown('### 攏總')
df_monthly_total = df_raw.groupby(
   by=C.COL_YM,
   as_index=False
)[C.COL_AMOUNT].agg('sum')
max_amount_in_ban7 = math.ceil(df_monthly_total[C.COL_AMOUNT].max() / 1E4)
fig_monthly_total = go.Figure(go.Scatter(
   name=C.COL_AMOUNT,
   mode='markers',
   x=df_monthly_total[C.COL_YM],
   y=df_monthly_total[C.COL_AMOUNT],
   marker=dict(
      size=16
   )
))
fig_monthly_total.add_trace(go.Scatter(
   name=f'{num_months_focus}個月移動平均',
   mode='lines',
   x=df_monthly_total[C.COL_YM],
   y=df_monthly_total[C.COL_AMOUNT].rolling(num_months_focus, min_periods=1).mean(),
   line=dict(
      width=6
   )
))
fig_monthly_total.update_yaxes(
   title_text='萬',
   gridwidth=0.1,
   tickmode='array',
   tickvals=[i * 1E4 for i in range(max_amount_in_ban7 + 1)],
   ticktext=list(range(max_amount_in_ban7 + 1)),
   tickfont_size=FONT_SIZE_TICK,
   tickwidth=10
)
fig_monthly_total.update_xaxes(
   title_text=C.COL_YM,
   showgrid=False,
   tickfont_size=FONT_SIZE_TICK
)
st.plotly_chart(fig_monthly_total, use_container_width=True)


# each month by group
st.markdown('#### 逐月分組')
fig_all_months = px.bar(
   data_frame=df_raw,
   x=C.COL_YM,
   y=C.COL_AMOUNT,
   color=col_group,
   color_discrete_map=get_color_map(col_group)
)
fig_all_months.update_yaxes(
   title_text='萬',
   gridwidth=0.1,
   tickmode='array',
   tickvals=[i * 1E4 for i in range(max_amount_in_ban7 + 1)],
   ticktext=list(range(max_amount_in_ban7 + 1)),
   tickfont_size=FONT_SIZE_TICK,
   tickwidth=10
)
fig_all_months.update_xaxes(
   tickfont_size=FONT_SIZE_TICK
)
st.plotly_chart(fig_all_months, use_container_width=True)


# recent few months by group
st.markdown(f'### 最近{num_months_focus}個月')
ym_center = st.selectbox(label=C.COL_YM, options=ym_list, index=num_months_total-1)

# todo: fix bug, now only support radius_months = 1
center_idx = ym_list.index(ym_center)
if center_idx == num_months_total - 1:
   center_idx -= 1
elif center_idx == 0:
   center_idx += 1
target_indices = list(range(center_idx - 1, center_idx + 2))
fig_subtitles = [
   f'<b>{ym}</b><br>${total}'
   for ym, total in zip(df_monthly_total[C.COL_YM], df_monthly_total[C.COL_AMOUNT])
]
fig_recent_months = make_subplots(
   rows=1, cols=num_months_focus,
   specs=[[{'type': 'pie'} for _ in range(num_months_focus)]],
   subplot_titles=[fig_subtitles[idx] for idx in target_indices]
)
for idx, ym in enumerate(ym_list[i] for i in target_indices):
   df_curr_month = df_raw.query(f'{C.COL_YM} == @ym')
   df_by_group = df_curr_month.groupby(
      by=col_group,
      as_index=False
   )[C.COL_AMOUNT].agg('sum')
   df_by_group[COL_PCT] = (
      df_by_group[C.COL_AMOUNT] / df_by_group[C.COL_AMOUNT].sum() * 1E2
   ).transform(lambda pct: f'{pct:.1f}')

   fig_by_group = px.pie(
      df_by_group,
      names=col_group,
      values=C.COL_AMOUNT,
      color=col_group,
      color_discrete_map=get_color_map(col_group),
      hover_data=[COL_PCT]
   )
   fig_by_group.update_traces(
      hovertemplate='%{customdata[0][1]}=%{customdata[0][0]}%<extra></extra>'
   )
   fig_recent_months.add_trace(
      fig_by_group.data[0],
      row=1, col=(idx + 1)
   )
fig_recent_months.update_traces(
   textposition='inside',
   textinfo='label+value',
   textfont_size=FONT_SIZE_TEXT,
   insidetextorientation='horizontal'
)
fig_recent_months.update_layout(
   hoverlabel=dict(font_size=FONT_SIZE_HOVER)
)
st.plotly_chart(fig_recent_months, use_container_width=True)


# monthly detail
st.markdown('#### 這月分組')
df_curr_month = df_raw.query(f'{C.COL_YM} == @ym_center')
df_by_group = df_curr_month.groupby(
   by=col_group,
   as_index=False
)[C.COL_AMOUNT].agg('sum')
df_by_group.sort_values(by=C.COL_AMOUNT, inplace=True)
num_classes = df_by_group[col_group].shape[0]

fig_curr_month = make_subplots(
   rows=1, cols=num_classes,
   specs=[[{'type': 'pie'} for _ in range(num_classes)]],
   subplot_titles=[
      f'<b>{cls}</b><br>${total}'
      for cls, total in zip(df_by_group[col_group], df_by_group[C.COL_AMOUNT])
   ]
)
for idx, cls in enumerate(df_by_group[col_group]):
   df_by_group = df_curr_month.query(f'{col_group} == @cls')
   df_by_tag = df_by_group.groupby(
      by=C.COL_TAG,
      as_index=False
   )[C.COL_AMOUNT].agg('sum')
   fig_curr_month.add_trace(
      go.Pie(
         labels=df_by_tag[C.COL_TAG],
         values=df_by_tag[C.COL_AMOUNT],
         textposition='inside',
         textinfo='label+value',
         textfont_size=FONT_SIZE_TEXT,
         insidetextorientation='horizontal',
         hoverinfo='label+percent',
         marker=dict(colors=HUES),
         showlegend=False
      ),
      row=1, col=(idx + 1)
   )
fig_curr_month.update_layout(
   hoverlabel=dict(font_size=FONT_SIZE_HOVER)
)
st.plotly_chart(fig_curr_month, use_container_width=True)
with st.expander('明細'):
   cols_detail = [
      C.COL_DD, C.COL_STORE, C.COL_ITEM, C.COL_AMOUNT, C.COL_TAG, col_group
   ]
   st.table(df_curr_month[cols_detail])


# customized query
st.markdown('### 家己來')
query = st.text_input(label='揣', placeholder=f"{C.COL_YM} == '{ym_list[-1]}'")
df_result = pd.DataFrame()
if query:
   df_result = df_raw.query(query)
if not df_result.empty:
   st.table(df_result)


### ===== Documentation ===== ###
st.header(HDR_DOC, anchor=hdr_to_id[HDR_DOC])
st.markdown(
   """
   ### 標
   - 租：月租
      - 蹛：(出遊)住宿、管理費
      - 水電：水、電、瓦斯、電信(網路)
      - 厝內：孝親費、幫家裡代買、紅包
   - 生活
      - 家具：非消耗品
      - 度日：消耗品
      - 植物
      - 穿插：含鞋子
      - 梳妝：保養品、剪髮
   - 煮食
      - 菜市：菜市場、水果行、希望廣場
      - 超市：大潤發、全聯
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
      - 通勤：捷運、UBike(抓關鍵字「悠遊卡儲值」)、GoShare
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
