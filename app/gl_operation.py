import pandas as pd
import numpy as np
from modify_case_code import CaseCode

balance_path = r"E:\RR\balance\0814.xlsx"
revenue_path = r"D:\账务处理\2023年\11月\业务收入明细 (2).xlsx"
result1 = r"E:\RR\result1.xlsx"
GLoffset = r"E:\RR\GLoff.xlsx"

t_gl = pd.read_excel(balance_path, dtype={"项目名称": str, "项目编码": str, "客户编码": str}).ffill(
    axis=0
)[
    ["科目编码", "科目名称", "项目名称", "项目编码", "客户编码", "客户名称", "期末余额金额"]
]  # deprecate "方向_"
t_gl = t_gl.loc[(t_gl["科目编码"] != 1221996) & (t_gl["项目编码"] != 0)]
t_gl["项目编码"] = t_gl["项目编码"].apply(lambda x: "AH." + str(x))
t_gl_0 = t_gl.copy()  ########ORIGIN

t_rr = pd.read_excel(revenue_path, header=[0, 2], sheet_name=r"2023年")
t_rr = t_rr.loc[7060:8046].fillna(0)  # excel行号-4
t_rr.iloc[:, 2] = t_rr.iloc[:, 2].apply(CaseCode)
t_rr = t_rr.iloc[:, [2, 14, 15]]
new_line = ["受案号", "收入", "增值税"]
t_rr = t_rr.set_index(pd.Series([i for i in range(t_rr.shape[0])]))
t_rr.columns = pd.Index(new_line)
t_rr["sett"] = 0.0


def settle(id):  # 冲预收
    df_rec = t_gl.loc[(t_gl["项目名称"] == t_rr.loc[id].受案号)].sort_values(by="期末余额金额")

    sett = -1 * (t_rr.loc[id].收入 + t_rr.loc[id].增值税) + 0.000001

    if df_rec["期末余额金额"].sum() + sett >= 0:
        Q = df_rec["期末余额金额"].tolist()
        Le = len(Q)

        try:
            while Q[0] + sett < 0:
                sett = sett + Q[0]
                Q.pop(0)

            Q[0] = Q[0] + sett
            Q = [0 * i for i in range(Le - len(Q))] + Q
            df_rec["期末余额金额"] = np.array(Q)

            t_rr.loc[id, "sett"] = 1.0
        except IndexError:
            print("Error, invoiced case adjustment")

    else:
        print("Error, please check")
    for id in df_rec.index.values:
        t_gl.loc[id, "期末余额金额"] = df_rec.loc[id, "期末余额金额"]
        print("Settled, please check the result")


for id in t_rr.index.values:
    print(id)
    settle(id)

t_gl_1 = t_gl.copy()

t_rr.to_excel(result1)
t_gl_offset = t_gl_0.copy()
t_gl_offset["g"] = t_gl_1["期末余额金额"]
t_gl_offset["diff"] = t_gl_offset["期末余额金额"] - t_gl_offset["g"]
t_gl_offset = t_gl_offset.loc[t_gl_offset["diff"] != 0].drop(["期末余额金额", "g"], axis=1)

t_rr.loc[t_rr["sett"] != 1.0]
t_gl_offset.to_excel(GLoffset)
