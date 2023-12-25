#!/usr/bin/env python
# -*- coding: utf-8 -*-
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
from custom_pages.case_fee_recon import case_fee_recon
from custom_pages.intro import intro
from custom_pages.case_rem import case_rem
from custom_pages.case_refund import case_refund
from custom_pages.case_gl_balance import case_gl_balance

# import pprint as pprint

st.set_page_config(page_title="Accouting")
page_names_to_funcs = {
    "首页": intro,
    "对账": case_fee_recon,
    "报酬": case_rem,
    "退费": case_refund,
    "总账余额": case_gl_balance,
}
with st.sidebar:
    st.title("Bank Reconciliaton & Case Info")

with open("../config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    config["preauthorized"],
)

authenticator.login("Login", "sidebar")

if st.session_state["authentication_status"]:
    authenticator.logout("Logout", "sidebar", key="unique_key")
    st.write(f'Welcome *{st.session_state["name"]}*')
    app_name = st.sidebar.selectbox("Choose a demo", page_names_to_funcs.keys())
    page_names_to_funcs[app_name]()

elif st.session_state["authentication_status"] is False:
    st.error("Username/password is incorrect")
elif st.session_state["authentication_status"] is None:
    st.warning("Please enter your username and password")
