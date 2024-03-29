#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
from zeep import Client, Settings
from zeep.cache import SqliteCache
from zeep.transports import Transport
from enum import Enum
import toml

with open("../credentials.toml") as f:
    conn_info = toml.load(f)

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
    LOGIN = r"http://192.168.130.6:6890/ormrpc/services/EASLogin?wsdl"
    CUSTOMER_OP = (
        r"http://192.168.130.6:6890/ormrpc/services/WSExportCustomerFacade?wsdl"
    )
    PROJECT_OP = r"http://192.168.130.6:6890/ormrpc/services/WSWSVoucher?wsdl"
    GL_OP = r"http://192.168.130.6:6890/ormrpc/services/WSGLWebServiceFacade?wsdl"


session = requests.session()
session.trust_env = False

settings = Settings(force_https=False)
transport = Transport(
    cache=SqliteCache(r"/home/scia/NewP/CaseFA/app/wsdlCache.db", timeout=3600),
    session=session,
)

eas_login_api = Client(WSDL_URL.LOGIN.value, transport=transport, settings=settings)

login_info = conn_info["EAS"]

customer_data_api = Client(
    WSDL_URL.CUSTOMER_OP.value, transport=transport, settings=settings
)

case_code_data_api = Client(
    WSDL_URL.PROJECT_OP.value, transport=transport, settings=settings
)
