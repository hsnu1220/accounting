import streamlit as st
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
from plotly import express as px
import consts as C
from utils import (
   get_df_cash,
   get_df_ctbc,
   get_df_citi,
   get_df_tsib,
   parse_spending_from_ctbc,
   trim_store,
   store_to_tag,
   tag_to_class
)
import math


# ================ #
# Global variables #
# ================ #
SHEET_ID_CASH = '1DNvY54rC1IaExN-xgnMYW3ru5lNXv0RjbqswakcGQh8'
SHEET_ID_CARD_CITI = '1_eIEiaS6IiKqTIrSVUaNqd5jtjO2M9IWa2zsPIOsYpQ'
SHEET_ID_CARD_TSIB = '1uM-1q8jDAgpPuyAdRVdWX97EXJAFmUkbtuXk8p0AqME'

COL_PCT = '比例'
HUES = px.colors.qualitative.Set3
FONT_SIZE_TICK = 16
FONT_SIZE_TEXT = 20
FONT_SIZE_HOVER = 16


# ================ #
# Helper functions #
# ================ #
def get_color_map(group=C.COL_CLASS):
   arr = C.CLASSES
   if group == C.COL_PAY:
      arr = C.PAYS
   elif group == C.COL_FREQ:
      arr = C.FREQS
   return {elm: hue for elm, hue in zip(arr, HUES)}


# =========== #
# Page config #
# =========== #
st.set_page_config(
   page_title=C.PAGE_TITLE,
   page_icon=C.PAGE_ICON,
   layout='wide',
   initial_sidebar_state='collapsed'
)


# ======== #
# Spending #
# ======== #
st.header(':shopping_trolley: 開')
df_out = pd.DataFrame()

# === Cash === #
df_cash = get_df_cash(SHEET_ID_CASH)
df_out = df_out.append(df_cash, ignore_index=True)

# === Bank === #
df_ctbc = get_df_ctbc(C.SHEET_ID_BANK_CTBC, ['2022'])
df_ctbc_spending = parse_spending_from_ctbc(df_ctbc)
df_out = df_out.append(df_ctbc_spending, ignore_index=True)

# === Credit card === #
df_citi = get_df_citi(SHEET_ID_CARD_CITI, ['2022'])
df_out = df_out.append(df_citi, ignore_index=True)

df_tsib = get_df_tsib(SHEET_ID_CARD_TSIB, ['2022'])
df_out = df_out.append(df_tsib, ignore_index=True)

# === Infer tag, class, freq === #
df_out[C.COL_DD] = df_out[C.COL_DD].astype('int32')
df_out[C.COL_STORE] = df_out[C.COL_STORE].transform(trim_store)
df_out[C.COL_AMOUNT] = df_out[C.COL_AMOUNT].astype('int32')
df_out.loc[df_out[C.COL_ITEM].str.contains('儲值'), C.COL_FREQ] = C.FREQ_TOPUP

df_out.loc[df_out[C.COL_TAG] == '', C.COL_TAG] = (
   df_out.loc[df_out[C.COL_TAG] == '', C.COL_STORE]
).transform(store_to_tag)
df_out[C.COL_CLASS] = df_out[C.COL_TAG].transform(tag_to_class)
df_out[C.COL_FREQ] = df_out[C.COL_FREQ].replace('', C.FREQ_ONCE)
df_out.sort_values(
   by=[C.COL_MM, C.COL_DD],
   inplace=True,
   ignore_index=True
)


# === Monthly summary === #
st.subheader('攏總')
df_monthly_total = df_out.groupby(
   by=C.COL_MM,
   as_index=False
)[C.COL_AMOUNT].agg('sum')
max_amount_in_ban7 = math.ceil(df_monthly_total[C.COL_AMOUNT].max() / 1E4)
fig_monthly_total = go.Figure()
is_by_group = st.checkbox(label='分組')
col_group = st.selectbox(
   label='照',
   options=[C.COL_CLASS, C.COL_FREQ, C.COL_PAY],
)
if not is_by_group:
   fig_monthly_total.add_trace(go.Scatter(
      name=C.COL_AMOUNT,
      mode='markers',
      x=df_monthly_total[C.COL_MM],
      y=df_monthly_total[C.COL_AMOUNT],
      marker=dict(
         size=16
      )
   ))
   fig_monthly_total.add_trace(go.Scatter(
      name='三個月平均',
      mode='lines',
      x=df_monthly_total[C.COL_MM],
      y=df_monthly_total[C.COL_AMOUNT].rolling(3, min_periods=1).mean(),
      line=dict(
         width=6
      )
   ))
else:
   fig_monthly_total = px.histogram(
      data_frame=df_out,
      x=C.COL_MM,
      y=C.COL_AMOUNT,
      color=col_group,
      color_discrete_map=get_color_map(col_group)
   )
fig_monthly_total.update_xaxes(
   title_text=C.COL_MM,
   showgrid=False,
   tickfont_size=FONT_SIZE_TICK
)
fig_monthly_total.update_yaxes(
   title_text='萬',
   gridwidth=0.1,
   tickmode='array',
   tickvals=[i * 1E4 for i in range(max_amount_in_ban7 + 1)],
   ticktext=list(range(max_amount_in_ban7 + 1)),
   tickfont_size=FONT_SIZE_TICK,
   tickwidth=10
)
st.plotly_chart(fig_monthly_total, use_container_width=True)


# === Recent months === #
st.subheader('最近')
ym_list = df_out[C.COL_MM].dropna().unique().tolist()
num_months_total = len(ym_list)
ym_idx_end = num_months_total - 1
ym_idx_start = max(ym_idx_end - 2, 0)

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
   for ym, total in zip(
      df_monthly_total[C.COL_MM], df_monthly_total[C.COL_AMOUNT]
   )
]
fig_recent_months = make_subplots(
   rows=1, cols=num_months_focus,
   specs=[[{'type': 'pie'} for _ in ym_indices]],
   subplot_titles=[fig_subtitles[idx] for idx in ym_indices]
)
for col_idx, ym_idx in enumerate(ym_indices):
   df_curr_month = df_out.query(f"{C.COL_MM} == '{ym_list[ym_idx]}'")
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


# === Single month === #
st.subheader('孤月')
ym_target = st.select_slider(
   label=C.COL_MM,
   options=ym_list,
   value=ym_list[ym_idx_end]
)
df_target_month = df_out.query(f'{C.COL_MM} == @ym_target')
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


# === Customized query === #
ex_group = df_by_group[col_group][0]
query = st.text_input(
   label='家己揣',
   value=f"{C.COL_MM} == '{ym_target}' & {col_group} == '{ex_group}'"
)
df_result = df_out.query(query)
if not df_result.empty:
   st.table(df_result.drop(
      columns=[col for col in C.COLS_TYPE if col != col_group])
   )
