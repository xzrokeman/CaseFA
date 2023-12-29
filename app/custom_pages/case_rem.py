import datetime
import swifter
import streamlit as st
import pandas as pd
from initDB import mySqlEngine, sqliteEngine
import numpy as np
from utils import filter_dataframe, CaseCode

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
    ]#.copy()
    
    
    now = datetime.datetime.now()

    # 将“t_extend_t”列与当前时间的差值计算出来
    rem_display["time_diff"] = abs(rem_display["t_extend_t"] - now)

    """# 筛选出差值最小的行
    rem_display = rem_display.loc[
        rem_display["time_diff"] == rem_display["time_diff"].min()
    ]
    """
    st.markdown("默认查询最近`30`天发放的报酬情况，完整报酬数据请查询老华南办案系统")
    rem_display = rem_display.loc[
        rem_display["time_diff"] <= datetime.timedelta(days=30)
    ]

    # 如果你不想在结果中包含'time_diff'列，可以删除它
    rem_display = rem_display.drop("time_diff", axis=1)
    
    
    rem_display["case_code_m"] = rem_display["case_code"].swifter.apply(CaseCode)

    case_code_map = pd.read_sql("select * from case_code_map", sqliteEngine)

    def find_case_code_number(case_code_m):
        try:
            return case_code_map.loc[
                case_code_map["case_code_m"] == case_code_m, "case_code_number"
            ].values[0]
        except IndexError:
            return np.nan

    # 应用find_case_code_number函数到df的case_code_m列，生成新的列case_code_number
    rem_display["case_code_number"] = rem_display["case_code_m"].swifter.apply(
        find_case_code_number
    )

    fee_type_mapping = {
        "1": "报酬",
        "2": "奖励",
        "3": "扣减",
        "4": "办案其它报酬",
        "5": "出差补助",
        "6": "专家报酬",
        "7": "异地办案支出",
        "8": "专家核阅",
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
            "case_code": st.column_config.TextColumn("案号", disabled=True),
            "p_name": st.column_config.TextColumn("仲裁员姓名", disabled=True),
            "typ": st.column_config.TextColumn("报酬类型", disabled=True),
            "should_rmb": st.column_config.NumberColumn(
                "应发金额", disabled=True, format="%.2f"
            ),
            "tax_rmb": st.column_config.NumberColumn(
                "代扣税金额", format="%.2f", disabled=True
            ),
            "extend_rmb": st.column_config.NumberColumn(
                "实发金额", format="%.2f", disabled=True
            ),
            "extend_t": st.column_config.DateColumn("会计确认应发日期", disabled=True),
            "t_extend_t": st.column_config.DateColumn("出纳确认已付日期", disabled=True),
            "case_code_m": st.column_config.TextColumn("调整案号"),
            "case_code_number": st.column_config.TextColumn("EAS编码"),
        },
    )
