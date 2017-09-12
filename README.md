# Flow Migration Suite integration for Ansible Tower

This script will allow your Ansible Tower instance to use servers that are stored in your Flow Migration Suite to run jobs against.

If you are setting this up with Ansible Tower you should follow the tutorial posted [here](https://tidal.zendesk.com/hc/en-us/articles/115000763627).

If you would like to learn more about how this script works directly you should continue reading below.


## Configure Environment Variables

You must provide login credentials for the Tidal Migrations API via environment variables.

- `TIDAL_DOMAIN`
- `TIDAL_EMAIL`
- `TIDAL_PASSWORD`

For example you could run the these three commands on the host running Ansible Tower to set these:

```
export TIDAL_DOMAIN=demo.tidalmg.com
export TIDAL_EMAIL=admin@tidalmigrations.com
export TIDAL_PASSWORD=yoursecurepasswordhere!
```

If you need to configure a proxy you can set the environment variables:

- `HTTP_PROXY`
- `HTTPS_PROXY`

This is needed if the script is running on a system that requires a proxy to reach your Flow Migration API.

## Configuration

A configuration file can optionally be provided to customize the results returned by the script. If no config file is provided the script will use the default values specified below.

In order to use the configuration file you must provide it's location via an environment variable. An example would be:

`export CONFIG_PATH=/root/tidal.yml`

An exmaple configuration file would look like this:

```
property: "fqdn"

groups:
  non-test:
    logic: None
    tags:
      - TEST
  production:
    logic: All
    tags:
      - PROD
      - Production

filter-tags:
  logic: Any
  tags:
    - TEST
```

### property
The `property` key is used to specify the property that will be used as the hostname for the servers.

Note that this property must be unique across all servers.

This parameter is optional, if it is not set the default value of `fqdn` will be used.

### groups
The `groups` key can be used to specify sets of tags to define one or more groups of servers.

This key has higher precedence than `filter-tags`; if the groups key is present it will use these paraemters over the filter-tags.

Each key for groups is any arbitrary name that will define the group in Ansible Tower. Each group accepts two keys.
 - The `tags` key is a list of strings that specify the names of the tags used to define the group.
 - The `logic` key accepts 3 values, `Any`, `All` and `None`.
   - `Any` specifies that any applications with one of the listed tags will be part of the group.
   - `All` specifies that any applications with all of the listed tags will be part of the group.
   - `None` species that any applications with none of the tags specified will be part of the group.
   - By default, if no `logic` key is specified, `All` is used.

This parameter is optional, if there is no key then the results will not be grouped.

### filter-tags

The `filter-tags` key can be used to filter all servers based on a set of tags.

This key has lower precedence than `groups`; if the groups key is specified these parameters will be ignored.

The accepted keys and structure for this tag is identical to the `groups`, just specify a `logic` and `tags` key directly.

This parameter is optional, if there is no key then all servers will be returned.
