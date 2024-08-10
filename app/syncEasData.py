#!/usr/bin/env python
# -*- coding: utf-8 -*-
from zeep.xsd import *
import base64, gzip
import json, xmltodict
import pandas as pd
from initDB import (
    #customer_data_api,
    case_code_data_api,
    login_info,
    mlogin,
    sqliteEngine,
    oracleEngine
)

mlogin(login_info)

column_names = {"fname_l2": "customer_name", "fnumber": "customer_code"}
# SOAP operations are damn slow, read the database(read-only) makes things much faster and more straightforward
customer_data = pd.read_sql_query(
        "SELECT * FROM T_BD_Customer", 
        oracleEngine
        )[["fname_l2", "fnumber"]].rename(columns=column_names).drop_duplicates(subset="customer_name")

case_code_zip = case_code_data_api.service.nGetAsstActs(
    json.dumps(
        {
            "asstActTypeNumber": "ZCY001",
            "isCompress": True,
            # "asstActNumber": "AH.00057652",
        }
    )
)

case_code_json = gzip.decompress(base64.b64decode(case_code_zip)).decode()

case_code_data = pd.DataFrame(
    [
        dict(case_code_m=row["name"], case_code_number=row["longNumber"])
        for row in json.loads(case_code_json)["rows"]
    ]
).drop_duplicates(subset="case_code_m")

with sqliteEngine.connect() as sconn:
    customer_data.to_sql("customer_map", sconn, index=False, if_exists="replace")
    case_code_data.to_sql("case_code_map", sconn, index=False, if_exists="replace")
