import streamlit as st
import pandas as pd
from connectivty.db_conn import sqliteEngine
from utils import filter_dataframe, transform_case_code


def case_fee_recon():
    st.write("本地缓存收款记录")

    # @st.cache_data
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
    df_n["case_code"] = df_n["case_code"].fillna(df_n["bill_code"])
    df_n.index = range(1, len(df_n) + 1)
    df_n = transform_case_code(df_n)
    #st.write(df_n.columns)
    st.dataframe(
        filter_dataframe(df_n),
        hide_index=False,
        # num_rows="dynamic",
        use_container_width=True,
        height=600,
        column_config={
            "u_t": st.column_config.DatetimeColumn("收款时间", disabled=True),
            "txnamt": st.column_config.NumberColumn("收款金额", format="%.2f"),
            "case_code_m": st.column_config.TextColumn("调整案号"),
        },
    )
    ###############################################################################
    case_code_map = pd.read_sql("select * from case_code_map", sqliteEngine)

    customer_map = pd.read_sql("select * from customer_map", sqliteEngine)

    c1, c2 = st.columns(2)
    with c1:
        st.dataframe(customer_map)

    with c2:
        st.dataframe(case_code_map)
