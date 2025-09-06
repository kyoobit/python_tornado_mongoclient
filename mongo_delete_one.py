import logging
import json

from pathlib import Path

# https://pymongo.readthedocs.io/en/stable/
from bson.objectid import ObjectId
from bson.errors import InvalidId

# https://www.tornadoweb.org/en/stable/
import tornado.web

from mongo_jsonencoder import ExtendedJSONEncoder


class DeleteOneHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        """Delete a single document matching the filter"""
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

        # Require a valid ObjectId ('_id') in request arguments
        try:
            objectid = self.request.arguments.get("_id", [b"-"])[-1].decode()
            objectid = ObjectId(objectid)
        except InvalidId:
            logging.warning(
                f"{name} get - Invalid ObjectId ('_id') in request arguments"
            )
            self.set_status(400)
            return

        # Set a query filter that matches the document to delete.
        document = {"filter": {"_id": objectid}}
        logging.info(
            f"{collection.database.name}.{collection.name}.delete_one({document!r})"
        )

        # Delete a single document matching the filter.
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html#pymongo.asynchronous.collection.AsyncCollection.delete_one
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.DeleteResult
        result = await collection.delete_one(**document)
        response.update(count=1)
        response.update(result=[result])
        if self.settings.get("debug", False):
            self.set_header("X-Debug", "route=DeleteOneHandler.get")
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
