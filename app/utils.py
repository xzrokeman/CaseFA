import re, datetime
import pandas as pd
import polars as pl
import streamlit as st
from pandas.api.types import (
    is_categorical_dtype,
    is_datetime64_any_dtype,
    is_numeric_dtype,
    is_object_dtype,
)
from functools import reduce
from typing import Tuple

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
                    df = df.loc[df[column].between(start_date, end_date+datetime.timedelta(days=1))]
            else:
                user_text_input = right.text_input(
                    f"Substring or regex in {column}",
                )
                if user_text_input:
                    df = df[df[column].str.contains(user_text_input)]

    return df

def CaseCode(string: str) -> str:
    def CasePrefix(string):
        if "medical" in string:
            return "yl"
        elif "sforeign" in string:
            return "sw"
        elif "sz" in string:
            return "sz"
        elif "international" in string:
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
    pl.when(pl.col("year").cast(pl.Int32)>2099)
    .then(pl.col('case_code'))
    .otherwise(pl.concat_str([pl.col("prefix"), pl.col("year"), pl.col("code")])).alias('case_code_m'),
    ).drop(['year','code','a','prefix']).collect().to_pandas().astype(str)
    return df1

def consume(
        stock: pl.Series, 
        utilization: pl.Series
        ) -> pl.Series:
    used = []
    # Allow OVERDRAFT by default! We will check insufficient stock later
    if stock.sum() < 0 or utilization.sum() < 0:
        used.append(utilization.cast(pl.Float64).round(2).sum())
    else:
        n = 0
        consumption = utilization.sum()
        while n <= stock.shape[0]:
            if stock.sum() > utilization.sum():
                if consumption - stock[n] > 0:
                    used.append(stock[n])
                    consumption -= stock[n]
                else:
                    used.append(consumption)
                    if n < stock.shape[0] - 1:
                        used = used + [None] * (stock.shape[0]-n-1)
                    break
                n += 1
            # Allow OVERDRAFT by default! We will check insufficient stock later
            else:
                if stock.len() <= 1:
                    used.append(consumption)
                    break
                else:
                    x = stock.to_list()[0:-1]
                    y = utilization.sum() - sum(x)
                    used = x + [y]
                    break
    return pl.Series(name="used", values=used).cast(pl.Float64)

# p1 = pl.Series(name="p1", values=[100, 2000,305.0]).cast(pl.Float64)
# p2 = pl.Series(name="p2", values=[500.0]).round(2)
# consume(p1,p2).sum()
# 500.0

def batch_proc(
        gl_bal: pl.DataFrame, 
        batch: pl.DataFrame) -> Tuple[pl.DataFrame,pl.DataFrame]:
    unique_series: pl.Series = batch.select(pl.col("项目名称")).to_series().unique()
    used:list = []
    for code in unique_series:
        pool: pl.DataFrame = gl_bal.filter(pl.col("项目名称") == code).clone()
        req: pl.DataFrame = batch.filter(pl.col("项目名称") == code).clone()
        use: pl.Series = consume(
            pool.select(pl.col("金额")).to_series(),
            req.select(pl.col("金额")).to_series()
        )
        used.append(pool.with_columns(use))
    usedf: pl.DataFrame = pl.concat(used, how="vertical")
    check_df: pl.DataFrame = batch.group_by("项目名称").agg(pl.sum("金额").alias("offset")).join(
        gl_bal.group_by("项目名称").agg(pl.sum("金额").alias("bal")),
        on="项目名称",
        how="left"
        ).with_columns(
            (pl.col("bal")-pl.col("offset")).round(2).alias("diff")
            ).filter(
                pl.col("diff") < 0
            )
    return usedf.drop_nulls(), check_df
