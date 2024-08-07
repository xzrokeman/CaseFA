#!/usr/bin/env python
# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from urllib.parse import quote_plus
import toml
import oracledb

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

lib_dir = conn_info['eas_db']['lib_dir']
# Connecting Oracle 11g requires oracledb client or at least oracle-instant-client installed,
# the client software can be found on official website.
# For oracleDB before version 12.1, you need to activate "Thick Mode"
# through calling `oracledb.init_oracle_client(lib_dir)`.
# "lib_dir" is where you place your oracle-instant-client.
oracledb.init_oracle_client(lib_dir)
DIALECT = conn_info['eas_db']['DIALECT']
SQL_DRIVER = conn_info['eas_db']['SQL_DRIVER']
USERNAME = conn_info['eas_db']['USERNAME']
PASSWORD = conn_info['eas_db']['PASSWORD']
HOST = conn_info['eas_db']['HOST']
PORT = conn_info['eas_db']['PORT']
SERVICE = conn_info['eas_db']['SERVICE']

ENGINE_PATH_WIN_AUTH = DIALECT + '+' + SQL_DRIVER + '://' + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + str(PORT) + '/?service_name=' + SERVICE

oracleEngine = create_engine(
    ENGINE_PATH_WIN_AUTH,
    pool_recycle=3600,
    echo=True
    ) 
