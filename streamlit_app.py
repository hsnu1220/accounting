import streamlit as st
# import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px
import consts as C
from utils import get_google_sheet
import math


### ===== Global variables ===== ###
HDR_OUT = '支出'
HDR_NET = '滿月記帳表'

hdr_to_id = dict()
hdr_to_id[HDR_OUT] = 'spending'
hdr_to_id[HDR_NET] = 'accounting'

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
   layout='wide',
   initial_sidebar_state='collapsed'
)


### ===== Sidebar ===== ###
st.sidebar.markdown(
   f"""
   ## 目錄
   - [{HDR_NET}](#{hdr_to_id[HDR_NET]})
   - [{HDR_OUT}](#{hdr_to_id[HDR_OUT]})
   """,
   unsafe_allow_html=True
)
st.sidebar.header('分組')
col_group = st.sidebar.radio(
   label='照',
   options=[C.COL_CLASS, C.COL_PAY, C.COL_FREQ],
)


### ===== Monthly accounting ===== ###
st.header(HDR_NET, anchor=hdr_to_id[HDR_NET])
st.markdown(':construction: :construction_worker: :construction:')


### ===== Spending ===== ###
st.header(HDR_OUT, anchor=hdr_to_id[HDR_OUT])
df_raw = get_google_sheet(id=SHEET_ID, name=SHEET_NAME)
ym_list = df_raw[C.COL_YM].dropna().unique().tolist()
num_months_total = len(ym_list)
ym_idx_end = num_months_total - 1
ym_idx_start = max(ym_idx_end - 2, 0)


column_monthly_left, column_monthly_right = st.columns(2)

# monthly total
with column_monthly_left:
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
      name='平均',
      mode='lines',
      x=df_monthly_total[C.COL_YM],
      y=df_monthly_total[C.COL_AMOUNT].rolling(3, min_periods=1).mean(),
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
with column_monthly_right:
   st.markdown('### 逐月分組')
   fig_all_months = px.histogram(
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
st.markdown('### 最近')
ym_start, ym_end = st.select_slider(
   label='範圍',
   options=ym_list,
   value=(ym_list[ym_idx_start], ym_list[ym_idx_end])
)
ym_idx_start, ym_idx_end = map(
   lambda ym: ym_list.index(ym), [ym_start, ym_end]
)
num_months_focus = ym_idx_end - ym_idx_start + 1
ym_indices = list(range(ym_idx_start, (ym_idx_end + 1)))
fig_subtitles = [
   f'<b>{ym}</b><br>${total}'
   for ym, total in zip(df_monthly_total[C.COL_YM], df_monthly_total[C.COL_AMOUNT])
]
fig_recent_months = make_subplots(
   rows=1, cols=num_months_focus,
   specs=[[{'type': 'pie'} for _ in ym_indices]],
   subplot_titles=[fig_subtitles[idx] for idx in ym_indices]
)
for col_idx, ym_idx in enumerate(ym_indices):
   df_curr_month = df_raw.query(f"{C.COL_YM} == '{ym_list[ym_idx]}'")
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
      row=1, col=(col_idx + 1)
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
st.markdown('### 孤月')
ym_target = st.select_slider(
   label=C.COL_YM,
   options=ym_list,
   value=ym_list[ym_idx_end]
)
df_target_month = df_raw.query(f'{C.COL_YM} == @ym_target')
df_by_group = df_target_month.groupby(
   by=col_group,
   as_index=False
)[C.COL_AMOUNT].agg('sum')
df_by_group.sort_values(
   by=C.COL_AMOUNT,
   ascending=False,
   inplace=True,
   ignore_index=True
)
num_classes = df_by_group[col_group].shape[0]

fig_target_month = make_subplots(
   rows=1, cols=num_classes,
   specs=[[{'type': 'pie'} for _ in range(num_classes)]],
   subplot_titles=[
      f'<b>{cls}</b><br>${total}'
      for cls, total in zip(df_by_group[col_group], df_by_group[C.COL_AMOUNT])
   ]
)
for idx, cls in enumerate(df_by_group[col_group]):
   df_target_group = df_target_month.query(f'{col_group} == @cls')
   df_by_tag = df_target_group.groupby(
      by=C.COL_TAG,
      as_index=False
   )[C.COL_AMOUNT].agg('sum')
   fig_target_month.add_trace(
      go.Pie(
         labels=df_by_tag[C.COL_TAG],
         values=df_by_tag[C.COL_AMOUNT],
         textposition='inside',
         textinfo='label+value',
         textfont_size=FONT_SIZE_TEXT,
         insidetextorientation='horizontal',
         hoverinfo='label+percent',
         marker=dict(
            colors=px.colors.qualitative.Antique
         ),
         showlegend=False
      ),
      row=1, col=(idx + 1)
   )
fig_target_month.update_layout(
   hoverlabel=dict(font_size=FONT_SIZE_HOVER)
)
st.plotly_chart(fig_target_month, use_container_width=True)


# customized query
ex_group = df_by_group[col_group][0]
query = st.text_input(
   label='家己揣',
   value=f"{C.COL_YM} == '{ym_target}' & {col_group} == '{ex_group}'"
)
df_result = df_raw.query(query)
if not df_result.empty:
   st.table(df_result.drop(columns=[col_group]))
