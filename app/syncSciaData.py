#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas as pd
from initDB import mySqlEngine, sqliteEngine


# Case fee info from SCIA old website
def sync_case_fee_data():
    remote_frame = pd.read_sql(
        "select * from v_bank_records", mySqlEngine, dtype={"u_t": str}
    )

    # 从本地SQLite数据库获取原始数据
    local_frame = pd.read_sql("select * from v_bank_records", sqliteEngine)
    local_frame["u_t"] = local_frame["u_t"].astype("string")
    # 将远程数据和本地数据进行合并（去重）
    merged_frame = pd.concat([local_frame, remote_frame]).drop_duplicates(
        subset=["u_t", "txnamt", "ibkname", "acntname", "bill_code"], keep="last"
    )

    # 将合并后的数据更新到本地SQLite数据库
    with sqliteEngine.connect() as sconn:
        merged_frame.to_sql("v_bank_records", sconn, index=False, if_exists="replace")


# sync Kingdee EAS base data
if __name__ == "__main__":
    sync_case_fee_data()
"""
# 定时任务每2分钟执行一次数据同步
schedule.every(2).minutes.do(sync_data)

# 运行定时任务
while True:
    schedule.run_pending()
    time.sleep(1)
"""
