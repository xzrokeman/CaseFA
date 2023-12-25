import streamlit as st
import pandas as pd
import numpy as np
from initDB import mySqlEngine, sqliteEngine
import datetime
from modify_case_code import CaseCode


def case_refund():
    refund_bill = pd.read_sql("select * from refund_bill", mySqlEngine)
    # for debugging
    # st.dataframe(refund_bill)

    refund_display = refund_bill\
        .loc[refund_bill["state"] == 2]\
        .loc[
        :,
        [
            "case_code",
            "litigant_type",
            "litigant_name",
            "received_amount",
            "refund_amount",
            "refund_date",
            "create_time",
        ],
    ].copy()

    now = datetime.datetime.now()

    # Calc timedelta between t_extend_t and now
    refund_display["time_diff"] = abs(refund_display["create_time"] - now)

    # filter: get the most recent records that has been confirmed refundable
    # drop column 'time_diff'
    refund_display = (
        refund_display.loc[refund_display["time_diff"] <= datetime.timedelta(days=30)]
        .loc[refund_display["refund_date"].isna() == True]
        .drop("time_diff", axis=1)
    )

    refund_display["case_code_m"] = refund_display["case_code"].apply(CaseCode)

    case_code_map = pd.read_sql("select * from case_code_map", sqliteEngine)

    def find_case_code_number(case_code_m):
        try:
            return case_code_map.loc[
                case_code_map["case_code_m"] == case_code_m, "case_code_number"
            ].values[0]
        except IndexError:
            return np.nan

    # modify case code
    refund_display["case_code_number"] = refund_display["case_code_m"].apply(
        find_case_code_number
    )
    refund_display["litigant_type"] = refund_display["litigant_type"].astype(str)
    litigant_type_mapping = {"1": "申请人", "2": "被申请人"}

    refund_display["litigant_type"] = refund_display["litigant_type"].map(
        litigant_type_mapping
    )
    # alter index
    refund_display = refund_display.reset_index(drop=True)
    refund_display.index = range(1, len(refund_display) + 1)

    st.data_editor(
        refund_display,
        height=600,
        use_container_width=True,
        column_config={
            "case_code": st.column_config.TextColumn(
                "案号",
                disabled=True,
            ),
            "create_time": st.column_config.DateColumn("申请时间", disabled=True),
            "refund_date": st.column_config.DateColumn("会计确认时间", disabled=True),
            "received_amount": st.column_config.NumberColumn("收费金额", format="%.2f"),
            "refund_amount": st.column_config.NumberColumn("退费金额", format="%.2f"),
        },
        hide_index=False,
        num_rows="dynamic",
    )