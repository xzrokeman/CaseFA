import streamlit as st
import pandas as pd
import numpy as np
from initDB import mySqlEngine, sqliteEngine
import datetime
from utils import CaseCode
from .case_gl_balance import params, get_balance
from decimal import Decimal

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
    
    # query GL to check refundability #######################################################
    refund_display["sett"] = 0.0
    refund_display["bgl"] = 0.0
    balance_data = get_balance(params).fillna(0)
    balance_data['期未余额(本位币)'] = balance_data['期未余额(本位币)'].astype("float64")
    def settle(id):
        df_rec = balance_data\
            .loc[(
                balance_data['项目（案件案号）名称']==refund_display.loc[id, "case_code_m"]
                )]\
            .sort_values(by='期未余额(本位币)')
        # 期“未”余额……真不愧是你啊阿金  #-_-|||
        sett = refund_display.loc[id,"refund_amount"]
        refund_display.loc[id, 'bgl'] = df_rec['期未余额(本位币)'].sum() * -1
        if df_rec['期未余额(本位币)'].sum() + sett <= 0.0:
            Q = df_rec["期未余额(本位币)"].tolist()
            Le = len(Q)
            
            try:
                while Q[0] + sett > 0:
                    sett = sett + Q[0]
                    Q.pop(0) 
                
                Q[0] = Q[0] + sett
                Q = [0*i for i in range(Le-len(Q))]+Q
                df_rec["期未余额(本位币)"] = np.array(Q)
                refund_display.loc[id,'sett'] = 1.0
            except IndexError:
                print("Error, invoiced case adjustment")
            
        else:
            print("Insufficient fund!!!")
        for id in df_rec.index.values:
            balance_data.loc[id, "期未余额(本位币)"] = df_rec.loc[id, "期未余额(本位币)"]
            print("Settled, please check the result")
        
    for id in refund_display.index.values:
        settle(id)
    # end of refundability check ############################################
    

    st.data_editor(
        refund_display,
        height=800,
        use_container_width=True,
        column_config={
            "case_code": st.column_config.TextColumn(
                "案号",
                disabled=True,
                ),
            "create_time": st.column_config.DateColumn(
                "申请日期", 
                disabled=True
                ),
            "refund_date": st.column_config.DateColumn(
                "会计确认日期", 
                disabled=True
                ),
            "received_amount": st.column_config.NumberColumn(
                "收费金额", 
                format="%.2f"
                ),
            "refund_amount": st.column_config.NumberColumn(
                "退费金额", 
                format="%.2f"
                ),
        },
        hide_index=False,
        num_rows="dynamic",
        column_order=(
            "case_code",
            "litigant_type",
            "litigant_name",
            "received_amount",
            "refund_amount",
            "create_time",
            "case_code_m",
            "case_code_number",
            "sett",
            "bgl",
        )
    )
