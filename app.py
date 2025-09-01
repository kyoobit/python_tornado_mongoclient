import asyncio
import logging
import json

from pathlib import Path

# https://www.tornadoweb.org/en/stable/
import tornado.web
from tornado.log import access_log

# https://pymongo.readthedocs.io/en/stable/
from pymongo import AsyncMongoClient

from mongo_find import FindHandler


def log_function(handler, *args, **kwargs):
    """Writes a completed HTTP request to the `access_log'

    See Also:
        https://www.tornadoweb.org/en/stable/web.html#application-configuration
    """
    if handler.get_status() == 404 or handler.get_status() < 400:
        _log_method = access_log.info
    elif handler.get_status() < 500:
        _log_method = access_log.warning
    else:
        _log_method = access_log.error
    request_time = 1000.0 * handler.request.request_time()
    _log_method(
        "{status} {method} {full_url} {duration:0.2f}ms {forwarded}".format(
            status=handler.get_status(),
            method=handler.request.method,
            full_url=handler.request.full_url(),
            duration=request_time,
            forwarded=handler.request.headers.get("forwarded", "-"),
        )
    )


class DefaultHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} initialize - **kwargs: {kwargs!r}")
        self.set_header("Server", "Python/Tornado/MongoClient")

    def get(self, *args, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} get - *args: {args!r}")
        logging.debug(f"{name} get - **kwargs: {kwargs!r}")

        # Always return 204
        self.set_status(204)


class PingHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} initialize - **kwargs: {kwargs!r}")
        self.set_header("Server", "Python/Tornado/MongoClient")

    def get(self, *args, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} get - *args: {args!r}")
        logging.debug(f"{name} get - **kwargs: {kwargs!r}")

        # Always return 200 Pong!
        self.write({'ping': 'pong'})


class HealthCheckHandler(tornado.web.RequestHandler):

    def initialize(self, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} initialize - **kwargs: {kwargs!r}")
        self.set_header("Server", "Python/Tornado/MongoClient")

    def get(self, *args, **kwargs):
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} get - *args: {args!r}")
        logging.debug(f"{name} get - **kwargs: {kwargs!r}")

        raise NotImplementedError('HealthCheckHandler, ...work to do!')


def make_app(*args, **kwargs):
    name = f"{Path(__file__).name} -"

    # Read-only route handlers
    routes = [
        (r".*/find", FindHandler),
        (r".*/find_one", FindHandler),
        (r".*/healthcheck", HealthCheckHandler),
        (r".*/ping", PingHandler),
        (r"/.*", DefaultHandler),
    ]

    # Read-write route handlers
    if kwargs.get('--admin', False):
        routes += [
            #(r".*/insert_one", InsertOneHandler),
        ]

    # MongoDB PyMongo AsyncMongoClient
    # https://pymongo.readthedocs.io/en/4.13.0/api/pymongo/asynchronous/index.html
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/mongo_client.html
    logging.info(f"Using pymongo.AsyncMongoClient: {kwargs.get('mongodb', 'mongodb://127.0.0.1:27017')}")
    asyncmongoclient = AsyncMongoClient(kwargs.get('mongodb', 'mongodb://127.0.0.1:27017'),
        username=kwargs.get('username'),
        password=kwargs.get('password'),
        connectTimeoutMS=int(kwargs.get('connectTimeoutMS', 5000)), # driver default is 20000 ms
        serverSelectionTimeoutMS=int(kwargs.get('serverSelectionTimeoutMS', 5000)), # driver default is ???? ms
        appname=kwargs.get('appname', 'PyTornadoMongoClient'),
        )
    # Database connection to a specific document collection in a specific database
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/database.html
    database = asyncmongoclient.get_database(kwargs.get('database', 'test'))
    logging.debug(f"{name} make_app - database.name: {database.name!r}")
    # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html
    collection = database.get_collection(kwargs.get("collection", "test"))
    logging.debug(f"{name} make_app - collection.name: {collection.name!r}")

    ## 'default_query_filter' is a query document that selects which document(s) to include in the result set
    default_query_filter = json.loads(kwargs.get('default_query_filter', {}))
    logging.debug(f"{name} make_app - default_query_filter: {default_query_filter!r}")

    ## Initialize the default query options
    default_query_options = json.loads(kwargs.get('default_query_options', {}))
    logging.debug(f"{name} make_app - default_query_options: {default_query_options!r}")

    return tornado.web.Application(
        routes,
        asyncmongoclient=asyncmongoclient,
        collection=collection,
        debug=kwargs.get("debug", False),
        default_query_filter=default_query_filter,
        default_query_options=default_query_options,
        database=database,
        log_function=log_function,
    )


async def main(*args, **kwargs):
    name = f"{Path(__file__).name} - "
    logging.debug(f"{name} main - *args: {args}")
    logging.debug(f"{name} main - **kwargs: {kwargs}")

    app = make_app(**kwargs)
    app.listen(int(kwargs.get("port", 8888)))
    await asyncio.Event().wait()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
