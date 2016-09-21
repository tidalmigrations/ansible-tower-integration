#!/usr/bin/env python

import os
import requests
import sys
import json
import yaml
import argparse

def fail(msg):
    sys.stderr.write("%s\n" % msg)
    sys.exit(1)

class ApplicationInventory(object):

    def __init__(self):
        self.args = self._parse_cli_args()

    def run(self):
        self._get_env_vars()
        self._args = self._parse_cli_args()
        self.config_file = self._parse_config_file()
        self._set_default_config()

        ApplicationInventory.cookie = self.login()

        if self.groups is not None:
            output = self.get_group_servers()
        elif self._args.host is None:
            servers = self.get_servers()
            output = self.generate_data(servers)
        else:
            servers = self.get_server()
            output = self.generate_data(servers)

        self.output_data(output)

    def _get_env_vars(self):
        API_PREFIX = "/api/"
        self.config_path = os.environ.get('CONFIG_PATH')
        email = os.environ.get('APP_INV_EMAIL')
        password = os.environ.get('APP_INV_PASSWORD')
        domain = os.environ.get('APP_INV_DOMAIN')
        if domain and email and password:
            self.email = email
            self.domain = domain
            self.password = password
            self.api_url = "https://" + domain + API_PREFIX
        else:
            fail("You must provice three environment variables: APP_INV_EMAIL APP_INV_PASSWORD and APP_INV_DOMAIN. The value found for these thee variables was APP_INV_EMAIL: '%s' APP_INV_PASSWORD '%s' and APP_INV_DOMAIN '%s'" % (email, password, domain))

    def _parse_config_file(self):
        config = dict()
        if self.config_path:
            if self.config_path and os.path.exists(self.config_path):
                with open(self.config_path) as f:
                    try:
                        config = yaml.safe_load(f.read())
                    except Exception as exc:
                        fail("Error: parsing %s - %s" % (self.config_path, str(exc)))
        return config

    def _set_default_config(self):
        # Set the defaults for the config here. The defaults are used when there is no config file
        # or when there is no matching parameter in the config file.
        self.property = self.config_file.get("property", "fqdn")
        self.filter_tags = self.config_file.get("filter-tags", None)
        self.groups = self.config_file.get("groups", None)

    def _parse_cli_args(self):
        parser = argparse.ArgumentParser(
                description='Return Ansible inventory for one or more hosts via Application Inventory API')
        parser.add_argument('--list', action='store_true', default=True,
                           help='List all hosts (default: True)')
        parser.add_argument('--host', action='store',
                            help='Only get information for a specific host.')
        parser.add_argument('--pretty', action='store_true', default=False,
                           help='Pretty print JSON output(default: False)')
        return parser.parse_args()

    def login(self):
        login_uri = self.api_url + "login"
        body = {"email": self.email, "password": self.password}
        r = requests.post(login_uri, data = body)
        return r.cookies

    def get_servers(self):
        if self.filter_tags and self.filter_tags["tags"]:
            tags = []
            for t in self.filter_tags["tags"]:
                tags.append(self.get_tag(t))
            ids = ",".join(str(t) for t in tags)
            params = {"tag_ids":ids}
            if self.filter_tags["logic"]:
                params["query_type"] = self.filter_tags["logic"]
            else:
                params["query_type"] = "All"
            s = requests.get(self.api_url + "servers", params = params, cookies = self.cookie)
        else:
            s = requests.get(self.api_url + "servers", cookies = self.cookie)
        return s.json()[:100]

    def get_server(self):
        data = self.get_servers()
        data = filter(lambda s: s[self.property] == self._args.host, data)
        return data

    def get_group_servers(self):
        groups = self.get_tags()
        data = {}
        for g, props in groups.iteritems():
            tag_ids = ",".join([str(t["id"]) for t in props["tags"]])
            params = {"query_type": props["logic"], "tag_ids": tag_ids}
            s = requests.get(self.api_url + "servers", params = params, cookies = self.cookie)
            data[g] = s.json()
        hostvars = {}
        dev = 0
        for group, servers in data.iteritems():
            data[group] = []
            for s in servers:
                if s[self.property] is not None:
                    data[group].append(s[self.property])
                    hostvars[s[self.property]] = s
                dev += 1
                if dev > 98:
                    break

        response = data
        response["_meta"] = {"hostvars": hostvars}
        return response

    def get_tags(self):
        groups = {}
        for g, props in self.groups.iteritems():
            tags = []
            groups[g]= {}
            for t in props["tags"]:
                tags.append({"name": t, "id": self.get_tag(t)})
            groups[g]["tags"] = tags
            groups[g]["logic"] = props["logic"]
        return groups

    def get_tag(self, tag):
        r = requests.get(self.api_url + "tags", params = {"search" : tag}, cookies = self.cookie)
        return r.json()[0]["id"]

    def generate_data(self, data):
        if type(data) is list:
            servers = []
            hostvars = {}
            for s in data:
                if s[self.property] is not None:
                    servers.append(s[self.property])
                    hostvars[s[self.property]] = s
            return {"servers":{"hosts":servers}, "_meta": {"hostvars": hostvars}}

        else:
            return data

    def output_data(self, data):
        if self._args.pretty:
            print(json.dumps(data, sort_keys=True, indent=2))
        else:
            print(json.dumps(data))

ApplicationInventory().run()
