import logging
import json

from pathlib import Path

# https://www.tornadoweb.org/en/stable/
import tornado.web

from mongo_jsonencoder import ExtendedJSONEncoder
from mongo_query import build_query


class CountDocumentsHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        """Count documents in a collection matching a query"""
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

        # Build the database query for this request
        try:
            query = build_query(self.settings, self.request)
            logging.debug(f"{name} get - query: {query!r}")
        except ValueError as err:
            logging.warning(f"{name} get - {err!r}")
            self.set_status(400)
            return
        except BaseException:
            raise
        # While skip and limit are valid options, only keep the filter
        query = {"filter": query.get("filter", {})}
        logging.info(
            f"{collection.database.name}.{collection.name}.count_documents({query!r})"
        )

        # Query the database for matching documents
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html#pymongo.asynchronous.collection.AsyncCollection.count_documents
        count = await collection.count_documents(**query)
        response.update(count=count)
        if self.settings.get("debug", False):
            self.set_header("X-Debug", "route=CountDocumentskHandler.get")
            response.update(database=collection.database.name)
            response.update(collection=collection.name)
            response.update(query=query)
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
