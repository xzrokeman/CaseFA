#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from urllib.parse import quote_plus
import toml

with open("../credentials.toml") as f:
    conn_info = toml.load(f)

mySqlEngine = create_engine(
    f"mysql+pymysql://{conn_info['remote_db']['user_name']}:{quote_plus(conn_info['remote_db']['password'])}@{conn_info['remote_db']['url']}/{conn_info['remote_db']['database_name']}",
    pool_recycle=3600,
)

sqliteEngine = create_engine(
    "sqlite:///DataComposed.db?check_same_thread=False",
    poolclass=NullPool,
    echo=True,
)
