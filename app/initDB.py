#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from urllib.parse import quote_plus
from zeep import Client
from zeep.xsd import *
from urllib.parse import quote_plus
from enum import Enum
import toml

with open("../credentials.toml") as f:
    conn_info = toml.load(f)

mySqlEngine = create_engine(
    f"mysql+pymysql://{conn_info['remote_db']['user_name']}:{quote_plus(conn_info['remote_db']['password'])}@{conn_info['remote_db']['url']}/{conn_info['remote_db']['database_name']}",
    pool_recycle=3600,
)

sqliteEngine = create_engine(
    "sqlite:///DataComposed.db?check_same_thread=False", poolclass=NullPool, echo=True
)


# optional: using logging module to record the xml sent and received

import logging.config

logging.config.dictConfig(
    {
        "version": 1,
        "formatters": {"verbose": {"format": "%(name)s: %(message)s"}},
        "handlers": {
            "console": {
                "level": "DEBUG",
                "class": "logging.StreamHandler",
                "formatter": "verbose",
            },
        },
        "loggers": {
            "zeep.transports": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
            "zeep.Client": {
                "level": "DEBUG",
                "propagate": True,
                "handlers": ["console"],
            },
        },
    }
)


# EAS API meta data
class WSDL_URL(Enum):
    # Kingdee EAS 7.5 and above
    # f"https://{serverIP}:{port}/ormrpc/services/{serviceName}?/wsdl"
    LOGIN = r"http://192.168.0.1:6334/ormrpc/services/EASLogin?wsdl"
    CUSTOMER_OP = r"http://192.168.0.1:6334/ormrpc/services/WSExportCustomerFacade?wsdl"
    PROJECT_OP = r"http://192.168.0.1:6334/ormrpc/services/WSWSVoucher?wsdl"
    GL_OP = r"http://192.168.0.1:6334/ormrpc/services/WSGLWebServiceFacade?wsdl"


session = requests.session()
session.trust_env = False

eas_login_api = Client(WSDL_URL.LOGIN.value)

login_info = conn_info["EAS"]

customer_data_api = Client(WSDL_URL.CUSTOMER_OP.value)

case_code_data_api = Client(WSDL_URL.PROJECT_OP.value) 
