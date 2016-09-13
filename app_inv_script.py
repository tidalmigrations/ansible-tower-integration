#!/usr/bin/env python

import os
import requests
import json
import argparse

APP_INV_DOMAIN = os.environ['APP_INV_DOMAIN']
APP_INV_EMAIL = os.environ['APP_INV_EMAIL']
APP_INV_PASSWORD = os.environ['APP_INV_PASSWORD']

API_PREFIX = "/api/"
url = "http://" + APP_INV_DOMAIN + API_PREFIX

class ApplicationInventory(object):

    def __init__(self):
        self.args = self._parse_cli_args()

    def run(self):
        cookie = self.login()
        servers = self.get_servers(cookie)
        json = self.generate_data(servers)
        self.output_data(json)

    def _parse_cli_args(self):
        basename = os.path.splitext(os.path.basename(__file__))[0]
        default_config = basename + '.yml'

        parser = argparse.ArgumentParser(
                description='Return Ansible inventory for one or more hosts via Application Inventory API')
        parser.add_argument('--list', action='store_true', default=True,
                           help='List all containers (default: True)')
        parser.add_argument('--host', action='store',
                            help='Only get information for a specific container.')
        parser.add_argument('--pretty', action='store_true', default=False,
                           help='Pretty print JSON output(default: False)')
        parser.add_argument('--config-file', action='store', default=default_config,
                            help="Name of the config file to use. Default is %s" % (default_config))
        return parser.parse_args()

    def login(self):
        login_uri = url + "login"
        body = {"email": APP_INV_EMAIL, "password": APP_INV_PASSWORD}
        r = requests.post(login_uri, data = body)
        return r.cookies

    def get_servers(self, cookie):
        s = requests.get(url + "servers", cookies = cookie)
        return s.json()

    def generate_data(self, data):
        servers = []
        for s in data:
            if s["fqdn"] is not None:
                servers.append(s["fqdn"])
        return json.dumps({"servers":servers, "_meta":{"hostvars":servers}})

    def output_data(self, json):
        print(json)

ApplicationInventory().run()
