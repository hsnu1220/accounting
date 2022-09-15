import streamlit as st
import consts as C
from utils import (
   get_df_ctbc
)


# =========== #
# Page config #
# =========== #
st.set_page_config(
   page_title=C.PAGE_TITLE,
   page_icon=C.PAGE_ICON,
   layout='wide',
   initial_sidebar_state='collapsed'
)


# ====== #
# Income #
# ====== #
st.header(':moneybag: 儉')
st.markdown(':construction: :construction_worker: :construction:')
