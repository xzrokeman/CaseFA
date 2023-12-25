#!/usr/bin/env python
# -*- coding: utf-8 -*-
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader


with open("../config.yaml") as file:
    config = yaml.load(file, Loader=SafeLoader)

for user in config["credentials"]["usernames"]:
    config["credentials"]["usernames"][user]["password"] = (
        stauth.Hasher(config["credentials"]["usernames"][user]["password"])
        .generate()[0]
        .encode()
    )

with open("../config.yaml", "w") as f:
    yaml.dump(config, f)
