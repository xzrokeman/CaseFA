import streamlit as st
import pandas as pd
import json
from initDB import (
    login_info, 
    eas_login_api, 
    case_code_data_api,
    )

params = json.dumps(
        {
            "rptType": "AsstActBalance",
            "isComrepss": True,
            "companyNumber": "S01",
            "fromPeriodNumber": "202301",
            "toPeriodNumber": "202312",
            "currencyNumber": "BB01",
            # "accountNumber": "2251.001",
            "fromAccountNumber": "2241.006",
            "toAccountNumber": "2251.007",
            # "showAsstActLongNumber": True,
            "showAsstActName": True,
            "showFor": True,
            "showAsstActNumber": True,
            "showOnlyLeafAccount": True,
            "notShowZero": True,
            "balType": 1,
            "showLocal": True,
            "asstActTypes": [
                {"type": "ZCY001"}, 
                {"type": "00001"}, 
            ],
        },
    )

def get_balance(params:json):
    
    login_result = eas_login_api.service.login(**login_info)
    
    balance_data = case_code_data_api.service.nGetBalance(params)

    return pd.DataFrame(
        data=json.loads(balance_data)["rows"][3:],
        columns=json.loads(balance_data)["rows"][1],
    )

def case_gl_balance():
    balance_display = get_balance(params)
    balance_display["项目（案件案号）编码"] = balance_display["项目（案件案号）编码"].apply(
        lambda x: "AH." + x
    )
    balance_display["期未余额(本位币)"] = balance_display["期未余额(本位币)"].astype("float64") * -1
    # for debugging only
    #st.dataframe(balance_display)
    #st.write(balance_display.columns)
    balance_display.index = range(1, len(balance_display) + 1)

    with st.container(border=False):
        st.dataframe(
            balance_display,
            height=600,
            use_container_width=True,
            column_config={
                "期未余额(本位币)": st.column_config.NumberColumn(
                    "期末余额(本位币)",
                    format="%.2f",
                    ),
                },
            )
