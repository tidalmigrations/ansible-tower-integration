# Application Inventory integration for Ansible

This python script will populate ansible with a list of servers from the Application Inventory API.

## Configure Environment Variables

You must provide login credentials for the Application Inventory API via environment variables.

- `APP_INV_DOMAIN`
- `APP_INV_EMAIL`
- `APP_INV_PASSWORD`

For example you could run the these three commands on the host running Ansible Tower to set these:

```
export APP_INV_DOMAIN=appinvdemo.subdata.com
export APP_INV_EMAIL=admin@subdata.com
export APP_INV_PASSWORD=yoursecurepasswordhere!
```
## Configuration

A configuration file can optionally be provided to customize the results returned by the script. If no config file is provided the script will use the default values specified below. 

In order to use the configuration file you must provide it's location via an environment variable. An example would be:

`export CONFIG_PATH=/root/app_inv.yml`

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
