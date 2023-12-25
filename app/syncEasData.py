#!/usr/bin/env python
# -*- coding: utf-8 -*-
from zeep.xsd import *
from zeep.helpers import serialize_object
import base64, gzip
import json, xmltodict
import pandas as pd
from initDB import (
    customer_data_api,
    case_code_data_api,
    login_info,
    eas_login_api,
    sqliteEngine,
)

result_login = eas_login_api.service.login(**login_info)

result_customer_data = customer_data_api.service.exportCustomerData(1, 30000)

customer_list = []
for odict in serialize_object(result_customer_data):
    ndict = xmltodict.parse(odict["_value_1"])
    customer_list.append(
        {
            "customer_name": ndict["DataInfo"]["DataHead"]["name"],
            "customer_code": ndict["DataInfo"]["DataHead"]["number"],
        }
    )

customer_data = pd.DataFrame(customer_list).drop_duplicates(subset="customer_name")

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
