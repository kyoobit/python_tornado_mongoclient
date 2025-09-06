import logging
import json

from datetime import datetime, timezone
from pathlib import Path

# https://www.tornadoweb.org/en/stable/
import tornado.web

from mongo_jsonencoder import ExtendedJSONEncoder
from mongo_operator import operator_value


class InsertOneHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        """Selects one or more documents in a collection matching a query"""
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} get - *args: {args!r}")
        logging.debug(f"{name} get - **kwargs: {kwargs!r}")

        # Default response document
        response = {
            "count": 0,
            "result": [],
        }

        # Use the application database document collection
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html
        collection = self.settings.get("collection")

        # ...
        try:
            # Unpack and parse the request arguments
            document = {}
            for key, value in self.request.arguments.items():
                value = value[-1].decode()  # [..., b'value'] ---> 'value'
                key, value = operator_value(
                    key, value
                )  # 'field=$foo:bar' ---> 'field', {'$foo': ['bar']}
                document[key] = value
            logging.debug(f"{name} get - document: {document!r}")
        except ValueError as err:
            logging.warning(f"{name} get - {err!r}")
            self.set_status(400)
            return
        except BaseException:
            raise
        # Enforce using "now" for ctime/mtime
        now = datetime.now(tz=timezone.utc)
        document.update(ctime=now)
        document.update(mtime=now)
        logging.info(
            f"{collection.database.name}.{collection.name}.insert_one({document!r})"
        )

        # Query the database for matching documents
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html#pymongo.asynchronous.collection.AsyncCollection.insert_one
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.InsertOneResult
        result = await collection.insert_one(document)
        response.update(count=1)
        response.update(result=[result])
        if self.settings.get("debug", False):
            self.set_header("X-Debug", "route=InsertOneHandler.get")
            response.update(database=collection.database.name)
            response.update(collection=collection.name)
            response.update(document=document)
        # Normalize the response into a JSON formatted response
        self.set_header("Server", "Python/Tornado/MongoClient")
        self.set_header("Content-Type", "text/json")
        response = json.dumps(
            response,
            indent=4,
            separators=(",", ": "),
            sort_keys=True,
            cls=ExtendedJSONEncoder,
        )
        self.write(response + "\n")
