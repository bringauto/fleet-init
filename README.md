# Init script for BringAuto Fleet Management

Script for initialization of the [BringAuto Fleet Management] database - Script will delete all of the database content and fill up data from map json files

## Prerequisites:

- The [BringAuto Fleet Management] must be deployed and work

## Arguments

- -c or --config=`<file>` - config file (default: config/config.ini)
- -m or --maps=`<directory>` - directory with input files (default: maps/)
- -d or --delete - delete every entity in the database beforehand

## Config file

Example:

[DEFAULT]
pip
```ini
ApiKey = <ApiKey>
Url = localhost
Tenant = <TenantName>
```

### Sections

All parameters in `DEFAULT` section are required to let the script work.

## Build and run

Install requirements:

```
pip3 install -r requirements.txt
```

Example run:

```
python3 main.py -c config/config.ini -m maps -d
```

[BringAuto Fleet Management]: https://github.com/bringauto/fleet-management-http-api
