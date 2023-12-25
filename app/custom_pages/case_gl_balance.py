import streamlit as st
import pandas as pd
import json
from initDB import login_info, eas_login_api, case_code_data_api


def case_gl_balance():
    login_result = eas_login_api.service.login(**login_info)
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
            "asstActTypes": [
                {"type": "ZCY001"}, 
                {"type": "00001"}, 
            ],
        },
    )
    balance_data = case_code_data_api.service.nGetBalance(params)
    balance_display = pd.DataFrame(
        data=json.loads(balance_data)["rows"][3:],
        columns=json.loads(balance_data)["rows"][1],
    )
    balance_display["项目（案件案号）编码"] = balance_display["项目（案件案号）编码"].apply(
        lambda x: "AH." + x
    )
    st.dataframe(
        balance_display,
        height=600,
        use_container_width=True,
        column_config={
            "期末余额(原币)": st.column_config.NumberColumn(
                format="%.2f",
            ),
        },
    )
