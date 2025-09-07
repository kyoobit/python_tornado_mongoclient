# Python Tornado MongoClient

```shell
podman run --rm --interactive --tty --name mongoclient \
ghcr.io/kyoobit/tornado-mongoclient:latest --help
```
```
usage: cli.py [-h] [--port <int>] [--mongodb <uri>] [--username <str>]
    [--password <str>] [--database <str>] [--collection <str>]
    [--default-query-filter <str>] [--default-query-options <str>] [--admin]
    [--version] [--systemd] [--verbose] [--debug]

This is a Python Tornado Web MongoClient HTTP service.

Run the program:
  python3 ./cli.py
  python3 ./cli.py -v --port 8888

options:
  -h, --help            show this help message and exit
  --port <int>          Set the port to listen for HTTP traffic (default: 8888)
  --mongodb <uri>       Set the MongoDB URI (Default: mongodb://127.0.0.1:27017) environment variable MONGO_URI
  --username <str>      Set the MongoDB account username (Default to environment variable MONGO_USERNAME)
  --password <str>      Set the MongoDB account password (Default to environment variable MONGO_PASSWORD)
  --database <str>      Set the MongoDB database (Default to environment variable MONGO_DATABASE or 'test')
  --collection <str>    Set the MongoDB document collection (Default to environment variable MONGO_COLLECTION or 'test')
  --default-query-filter <str> A JSON document that sets default query filter (Default: "{}")
  --default-query-options <str> A JSON document that sets default query options (Default: "{}")
  --admin               Run with admin write routes enabled (Default: False)
  --version, -V         show program's version number and exit
  --systemd             Run with systemd service mode enabled
  --verbose, -v         Run with verbose messages enabled (Default: False)
  --debug               Run with noisy debug messages enabled (Default: False)
```

```shell
podman run --rm --detach --tty --publish 8892:8892/tcp --name mongoclient \
ghcr.io/kyoobit/tornado-mongoclient:latest --mongodb "${MONGO_URI}" \
--username "${MONGO_USERNAME}" --password "${MONGO_PASSWORD}" \
--database "${MONGO_DATABASE}" --collection "${MONGO_COLLECTION}" \
--default-query-filter '{"ctime":"$lte:$now"}' \
--default-query-options '{"limit":10,"sort":[["ctime",-1]]}' \
--verbose
```

