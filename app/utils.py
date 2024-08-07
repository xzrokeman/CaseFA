import re
import datetime
import pandas as pd
import streamlit as st
import polars as pl
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from functools import reduce

# this filter function comes from https://github.com/tylerjrichards/st-filter-dataframe/blob/main/streamlit_app.py

def filter_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds a UI on top of a dataframe to let viewers filter columns

    Args:
        df (pd.DataFrame): Original dataframe

    Returns:
        pd.DataFrame: Filtered dataframe
    """
    modify = st.checkbox("Add filters")

    if not modify:
        return df

    df = df.copy()

    # Try to convert datetimes into a standard format (datetime, no timezone)
    for col in df.columns:
        if is_object_dtype(df[col]):
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                pass

        if is_datetime64_any_dtype(df[col]):
            df[col] = df[col].dt.tz_localize(None)

    modification_container = st.container()

    with modification_container:
        to_filter_columns = st.multiselect("Filter dataframe on", df.columns)
        for column in to_filter_columns:
            left, right = st.columns((1, 20))
            left.write("↳")
            # Treat columns with < 10 unique values as categorical
            if is_categorical_dtype(df[column]) or df[column].nunique() < 10:
                user_cat_input = right.multiselect(
                    f"Values for {column}",
                    df[column].unique(),
                    default=list(df[column].unique()),
                )
                df = df[df[column].isin(user_cat_input)]
            elif is_numeric_dtype(df[column]):
                _min = float(df[column].min())
                _max = float(df[column].max())
                step = (_max - _min) / 100
                user_num_input = right.slider(
                    f"Values for {column}",
                    _min,
                    _max,
                    (_min, _max),
                    step=step,
                )
                df = df[df[column].between(*user_num_input)]
            elif is_datetime64_any_dtype(df[column]):
                user_date_input = right.date_input(
                    f"Values for {column}",
                    value=(
                        df[column].min(),
                        df[column].max(),
                    ),
                )
                if len(user_date_input) == 2:
                    user_date_input = tuple(map(pd.to_datetime, user_date_input))
                    start_date, end_date = user_date_input
                    df = df.loc[df[column].between(start_date, end_date)]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df


def CaseCode(string: str) -> str:
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


def transform_case_code(df: pd.DataFrame) -> pd.DataFrame:
    df1 = pl.from_pandas(df).lazy().with_columns(
    pl.col('case_code').str.extract_all(r"(\d*)").list.join("").alias('a')
    ).with_columns(
    pl.col('a').str.slice(0,4).alias("year"),
    pl.col('a').str.slice(4,5).alias("code"),
    pl.col('case_code').alias('origin')
    ).with_columns(
        prefix = pl.lit(None)
    ).with_columns(
        pl.col("code").str.zfill(4),
        pl.when(pl.col('case_code').str.contains("医疗"))
        .then(pl.col('prefix').fill_null("yl"))
        .when(pl.col('case_code').str.contains("深仲涉外"))
        .then(pl.col('prefix').fill_null("sw"))
        .when(pl.col('case_code').str.contains("深仲"))
        .then(pl.col('prefix').fill_null('sz'))
        .when(pl.col('case_code').str.contains("深国仲"))
        .then(pl.col('prefix').fill_null('gz'))
        .otherwise(pl.col('prefix').fill_null(""))
    ).with_columns(
# polars.Expr.cast(polars <= 0.20.27) is very similar to TRY_CAST in SQL, if you pass in strict=False, it 
# will return null for those that cannot be transformed, see example below:
#>>> import polars as pl
#>>> df = pl.DataFrame({"a": [1,2,3], "b": ["4", "5", "c"]})
#>>> df.with_columns(pl.col("b").cast(pl.Int32, strict=False))
#shape: (3, 2)
#┌─────┬──────┐
#│ a   ┆ b    │
#│ --- ┆ ---  │
#│ i64 ┆ i32  │
#╞═════╪══════╡
#│ 1   ┆ 4    │
#│ 2   ┆ 5    │
#│ 3   ┆ null │
#└─────┴──────┘
    pl.when(pl.col("year").cast(pl.Int32,strict=False)>2099)
    .then(pl.col('case_code').fill_null(pl.col('origin')))
    .otherwise(pl.concat_str([pl.col("prefix"), pl.col("year"), pl.col("code")])).alias('case_code_m'),
    ).drop(['year','code','a','prefix','origin']).collect().to_pandas().astype(str)
    return df1
