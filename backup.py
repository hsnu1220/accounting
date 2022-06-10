# ================ #
# streamlit_app.py #
# ================ #
hdr_to_id = dict()
hdr_to_id[HDR_OUT] = 'spending'
hdr_to_id[HDR_NET] = 'accounting'

# sidebar
st.sidebar.markdown(
   f"""
   ## 目錄
   - [{HDR_NET}](#{hdr_to_id[HDR_NET]})
   - [{HDR_OUT}](#{hdr_to_id[HDR_OUT]})
   """,
   unsafe_allow_html=True
)

# monthly accounting
st.header(HDR_NET, anchor=hdr_to_id[HDR_NET])
st.markdown(':construction: :construction_worker: :construction:')

st.header(C.HDR_OUT, anchor=hdr_to_id[HDR_OUT])


# ================ #
# Jupyter notebook #
# ================ #
import pandas as pd
pd.set_option('display.max_rows', None)

# [x] checked
col_ym = '年月'
col_dd = '日'
col_store = '店'
col_item = '項'
col_amount = '額'
col_tag = '標'
col_pay = '方式'
col_freq = '頻率'
col_class = '類'


# [x] checked
def get_class(store):
    if any(kw in store for kw in ['台哥大', '大台北瓦斯費']):
        return '月租'
    elif any(kw in store for kw in ['全聯', '大潤發', '家樂福']):
        return '煮食'
    elif any(kw in store for kw in ['麥味登', '萊爾富', '統一', '全家', '川川川川', '清心', '烏弄', '麥當勞', '休息站', '必勝客']):
        return '外食'
    elif any(kw in store for kw in ['悠遊付儲值', '中油', '加油站', '台塑石油', '台亞', '臺北市路邊', '大都會衛星']):
        return '交通'
    elif any(kw in store for kw in ['大創', '金興發', '康是美', '日藥本舖']):
        return '生活'
    elif any(kw in store for kw in ['宜家家居', '宜得利']):
        return '家具'
    elif any(kw in store for kw in ['威秀', '秀泰', '國家表演藝術中心', 'ＫＫＴＩＸ']):
        return '娛樂'
    else:
        return ''

# [x] 花旗

from datetime import date, timedelta
file_citi = 'citi.csv'

def prepend_year(mm_dd):
    # one_month_ago = date.today() - timedelta(days=32)
    # return f"{one_month_ago.strftime('%Y')}/{mm_dd}"
    dd, mm, yy = mm_dd.split('/')
    return '/'.join([yy, mm, dd])

def rm_substr(sr, kw, to_char=''):
    return sr.str.replace(f'\s*{kw}\s*', to_char, regex=True)

df_citi = pd.read_csv(
    file_citi,
    header=None,
    names=[col_date, col_store, col_amount],
    usecols=[0, 2, 3]
)
df_citi.dropna(subset=[col_amount], inplace=True)
df_citi.reset_index(drop=True, inplace=True)

df_citi[col_date] = df_citi[col_date].apply(prepend_year)

df_citi[col_store] = rm_substr(df_citi[col_store], '－', ' ')
for kw in ['TAIPEI', 'TW', 'CITY']:
    df_citi[col_store] = rm_substr(df_citi[col_store], kw)

df_citi[col_amount] = rm_substr(df_citi[col_amount], 'TWD')
df_citi[col_amount] = rm_substr(df_citi[col_amount], ',')
df_citi[col_amount] = df_citi[col_amount].astype(float)
df_citi[col_amount] = df_citi[col_amount].astype(int)

print(df_citi)

# [x] 中信

file_ctbc = 'ctbc.csv'
col_memo = '備註'
col_note = '註記'

def get_store(row):
    if row[col_memo] in ['街口', '悠遊付']:
        return f'{row[col_memo]}{row[col_note]}'
    else:
        return row[col_note]

def keep_note(s):
    return all(
        kw not in s for kw in ['花旗銀行信用卡', '阿魚', '渣打', '台新', '孝親', '房租']
    )

df_ctbc = pd.read_csv(
    file_ctbc,
    header=None,
    names=[col_date, col_amount, col_memo, col_note],
    usecols=[0, 2, 5, 7],
    encoding='big5'
)
df_ctbc.dropna(subset=[col_amount, col_note], inplace=True)
df_ctbc = df_ctbc[df_ctbc[col_note].apply(keep_note)]
df_ctbc[col_store] = df_ctbc.apply(get_store, axis=1)

df_ctbc.drop(columns=[col_memo, col_note], inplace=True)
df_ctbc.reset_index(drop=True, inplace=True)

print(df_ctbc)

# [x] 合併

file_both = 'cc.csv'

df = pd.concat([df_citi, df_ctbc])
df.sort_values(col_date, inplace=True, ignore_index=True)

df[col_item] = ''
df[col_class] = df[col_store].apply(get_class)

df = df[[col_date, col_store, col_item, col_amount, col_class]]
df.to_csv(file_both, index=False)
print(df)