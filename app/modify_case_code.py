import re
from functools import reduce


def CaseCode(string: str) -> str:  # 调整案号
    def CasePrefix(string):
        if "医疗" in string:
            return "yl"
        elif "深仲涉外" in string:
            return "sw"
        elif "深仲" in string:
            return "sz"
        elif "深国仲" in string:
            return "gz"
        else:
            return ""

    def CaseNum(string):
        if len(re.findall(r"\d+.?\d*", string)) == 0:
            return ""
        else:
            number_str = str(
                reduce(lambda x, y: x + y, re.findall(r"\d+\.?\d*", string))
            )
            if len(number_str) < 8:
                number_str = (
                    number_str[0:4] + "0" * (8 - len(number_str)) + number_str[4:]
                )
                return number_str
            elif len(number_str) == 8:
                return number_str[0:8]
            return number_str[0:9]

    return CasePrefix(string) + CaseNum(string)
