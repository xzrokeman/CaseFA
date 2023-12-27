import datetime
import streamlit as st
import pandas as pd
from initDB import mySqlEngine, sqliteEngine
from utils import CaseCode
import numpy as np


def case_rem():
    rem_data = pd.read_sql("select * from tb_extends", mySqlEngine)
    rem_display = rem_data.loc[
        :,
        [
            "case_code",
            "typ",
            "p_name",
            "should_rmb",
            "tax_rmb",
            "extend_rmb",
            "extend_t",
            "t_extend_t",
        ],
    ].copy()

    now = datetime.datetime.now()

    # 将“t_extend_t”列与当前时间的差值计算出来
    rem_display["time_diff"] = abs(rem_display["t_extend_t"] - now)

    # 筛选出差值最小的行
    rem_display = rem_display.loc[
        rem_display["time_diff"] == rem_display["time_diff"].min()
    ]

    rem_display = rem_display.drop("time_diff", axis=1)

    rem_display["case_code_m"] = rem_display["case_code"].apply(CaseCode)

    case_code_map = pd.read_sql("select * from case_code_map", sqliteEngine)

    def find_case_code_number(case_code_m):
        try:
            return case_code_map.loc[
                case_code_map["case_code_m"] == case_code_m, "case_code_number"
            ].values[0]
        except IndexError:
            return np.nan

    # 应用find_case_code_number函数到df的case_code_m列，生成新的列case_code_number
    rem_display["case_code_number"] = rem_display["case_code_m"].apply(
        find_case_code_number
    )

    fee_type_mapping = {
        "1": "case remuneration",
        "2": "bonus",
        "3": "deduction",
        "4": "other remuneration",
        "5": "travel expense",
        "6": "expert fee",
        "7": "travel expense premium",
        "8": "inspection fee",
    }

    rem_display["typ"] = rem_display["typ"].map(fee_type_mapping)

    rem_display = rem_display.reset_index(drop=True)
    rem_display.index = range(1, len(rem_display) + 1)

    st.data_editor(
        rem_display,
        hide_index=False,
        num_rows="fix",
        use_container_width=True,
        height=600,
        column_config={
            "case_code": st.column_config.TextColumn("case code", disabled=True),
            "p_name": st.column_config.TextColumn("expert name", disabled=True),
            "typ": st.column_config.TextColumn("rem type", disabled=True),
            "should_rmb": st.column_config.NumberColumn(
                "rem(before tax)", disabled=True, format="%.2f"
            ),
            "tax_rmb": st.column_config.NumberColumn(
                "tax", format="%.2f", disabled=True
            ),
            "extend_rmb": st.column_config.NumberColumn(
                "rem(after tax)", format="%.2f", disabled=True
            ),
            "extend_t": st.column_config.DateColumn("accountant confirm date", disabled=True),
            "t_extend_t": st.column_config.DateColumn("cashier confirm date", disabled=True),
            "case_code_m": st.column_config.TextColumn("modified case code"),
            "case_code_number": st.column_config.TextColumn("gl case number"),
        },
    )
