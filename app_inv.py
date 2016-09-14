#!/usr/bin/env python

import os
import requests
import sys
import json
import yaml
import argparse

APP_INV_DOMAIN = os.environ['APP_INV_DOMAIN']
APP_INV_EMAIL = os.environ['APP_INV_EMAIL']
APP_INV_PASSWORD = os.environ['APP_INV_PASSWORD']

API_PREFIX = "/api/"
url = "http://" + APP_INV_DOMAIN + API_PREFIX

def fail(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

class ApplicationInventory(object):

    def __init__(self):
        self.args = self._parse_cli_args()

    def run(self):
        self._args = self._parse_cli_args()
        self.config_file = self._parse_config_file()
        ApplicationInventory.cookie = self.login()
        if self._args.host is None:
            servers = self.get_servers()
        else:
            servers = self.get_server()

        output = self.generate_data(servers)
        self.output_data(output)

    def _parse_config_file(self):
        config = dict()
        config_path = None

        if self._args.config_file:
            config_path = self._args.config_file
        elif self._env_args.config_file:
            config_path = self._env_args.config_file

        if config_path:
            try:
                config_file = os.path.abspath(config_path)
            except:
                config_file = None

            if config_file and os.path.exists(config_file):
                with open(config_file) as f:
                    try:
                        config = yaml.safe_load(f.read())
                    except Exception as exc:
                        fail("Error: parsing %s - %s" % (config_path, str(exc)))
        return config

    def _parse_cli_args(self):
        basename = os.path.splitext(os.path.basename(__file__))[0]
        default_config = basename + '.yml'

        parser = argparse.ArgumentParser(
                description='Return Ansible inventory for one or more hosts via Application Inventory API')
        parser.add_argument('--list', action='store_true', default=True,
                           help='List all hosts (default: True)')
        parser.add_argument('--host', action='store',
                            help='Only get information for a specific host.')
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

    def get_servers(self):
        s = requests.get(url + "servers", cookies = self.cookie)
        return s.json()

    def get_server(self):
        data = self.get_servers()
        data = filter(lambda s: s[self.config_file["parsing"]["property"]] == self._args.host, data)
        return data

    def generate_data(self, data):
        if type(data) is list:
            servers = []
            for s in data:
                if s[self.config_file["parsing"]["property"]] is not None:
                    servers.append(s[self.config_file["parsing"]["property"]])
            return {"servers":servers, "_meta":{"hostvars":servers}}
        else:
            return data

    def output_data(self, data):
        if self._args.pretty:
            print(json.dumps(data, sort_keys=True, indent=2))
        else:
            print(json.dumps(data))

ApplicationInventory().run()
