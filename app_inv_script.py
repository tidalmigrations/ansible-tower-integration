#!/usr/bin/env python

import os
import requests
import json

APP_INV_DOMAIN = os.environ['APP_INV_DOMAIN']
APP_INV_EMAIL = os.environ['APP_INV_EMAIL']
APP_INV_PASSWORD = os.environ['APP_INV_PASSWORD']

API_PREFIX = "/api/"
url = "http://" + APP_INV_DOMAIN + API_PREFIX

def login():
    login_uri = url + "login"
    body = {"email": APP_INV_EMAIL, "password": APP_INV_PASSWORD}
    r = requests.post(login_uri, data = body)
    return r.cookies

def get_servers(cookie):
    s = requests.get(url + "servers", cookies = cookie)
    return s.json()

def generate_data(data):
    servers = []
    for s in data:
        if s["fqdn"] is not None:
            servers.append(s["fqdn"])
    return json.dumps({"servers":servers})

def output_data(json):
    print(json)

cookie = login()
servers = get_servers(cookie)
json = generate_data(servers)
output_data(json)
