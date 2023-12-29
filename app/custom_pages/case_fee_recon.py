import streamlit as st
import pandas as pd
from initDB import sqliteEngine
from utils import filter_dataframe

def case_fee_recon():
    st.write("本地缓存收款记录")

    #@st.cache_data
    def run_query(_engine):
        return pd.read_sql("select * from v_bank_records", _engine)

    df = run_query(_engine=sqliteEngine)
    df_n = df.loc[
        :,
        [
            "bill_code",
            "fee_type",
            "case_code",
            "pay_account",
            "acntname",
            "ibkname",
            "txnamt",
            "u_t",
            "furinfo",
        ],
    ].copy()
    df_n['case_code'] = df_n['case_code'].fillna(df_n['bill_code'])
    df_n.index = range(1, len(df_n) + 1)

    st.dataframe(
        filter_dataframe(df_n),
        hide_index=False,
        #num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "u_t": st.column_config.DatetimeColumn("收款时间", disabled=True),
            "txnamt": st.column_config.NumberColumn("收款金额", format="%.2f"),
        },
    )
