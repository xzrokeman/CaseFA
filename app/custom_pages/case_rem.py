import datetime
import streamlit as st
import pandas as pd
from connectivty.db_conn import mySqlEngine, sqliteEngine
from utils import filter_dataframe, transform_case_code


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
    ]  # .copy()

    now = datetime.datetime.now()

    rem_display["time_diff"] = abs(rem_display["t_extend_t"] - now)

    rem_display = rem_display.loc[
        rem_display["time_diff"] == rem_display["time_diff"].min()
    ]
    
    st.markdown("Query remunertaion paid in most recent `30` days.")
    rem_display = rem_display.loc[
        rem_display["time_diff"] <= datetime.timedelta(days=30)
    ]

    rem_display = rem_display.drop("time_diff", axis=1)

    rem_display = transform_case_code(rem_display)

    case_code_map = pd.read_sql("select * from case_code_map", sqliteEngine)
    
    rem_display = pd.merge(rem_display, case_code_map, on='case_code_m', how='left')

    fee_type_mapping = {
        "1": "remuneration",
        "2": "bonus",
        "3": "deduction",
        "4": "other_rem",
        "5": "traffic",
        "6": "expert_rem",
        "7": "non_local_traffic",
        "8": "award_review_rem",
    }

    rem_display["typ"] = rem_display["typ"].map(fee_type_mapping)

    rem_display = rem_display.reset_index(drop=True)
    rem_display.index = range(1, len(rem_display) + 1)

    st.data_editor(
        filter_dataframe(rem_display),
        hide_index=False,
        num_rows="fix",
        use_container_width=True,
        height=600,
        column_config={
            "case_code": st.column_config.TextColumn("CaseCode", disabled=True),
            "p_name": st.column_config.TextColumn("ArbitratorName", disabled=True),
            "typ": st.column_config.TextColumn("RemType", disabled=True),
            "should_rmb": st.column_config.NumberColumn(
                "AmountDue", disabled=True, format="%.2f"
            ),
            "tax_rmb": st.column_config.NumberColumn(
                "IncomeTax(personal)", format="%.2f", disabled=True
            ),
            "extend_rmb": st.column_config.NumberColumn(
                "AmountPayable", format="%.2f", disabled=True
            ),
            "extend_t": st.column_config.DateColumn("AccountantConfirmDate", disabled=True),
            "t_extend_t": st.column_config.DateColumn("CashierConfirmDate", disabled=True),
            "case_code_m": st.column_config.TextColumn(""),
            "case_code_number": st.column_config.TextColumn("EAS_code"),
        },
    )
