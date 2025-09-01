import logging
import json

from pathlib import Path

# https://www.tornadoweb.org/en/stable/
import tornado.web

from mongo_jsonencoder import ExtendedJSONEncoder
from mongo_query import build_query


class FindHandler(tornado.web.RequestHandler):
    async def get(self, *args, **kwargs):
        """Selects one or more documents in a collection matching a query"""
        name = f"{Path(__file__).name} -"
        logging.debug(f"{name} get - *args: {args!r}")
        logging.debug(f"{name} get - **kwargs: {kwargs!r}")

        # Default response document
        response = {
            'count': 0,
            'result': [],
        }

        # Use the application database document collection
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html
        collection = self.settings.get('collection')

        # Build the database query for this request
        try:
            query = build_query(self.settings, self.request)
            logging.debug(f"{name} get - query: {query!r}")
        except ValueError as err:
            logging.warning(f"{name} get - {err!r}")
            self.set_status(400)
            return
        except:
            raise
        logging.info(f"{collection.database.name}.{collection.name}.find({query!r})")

        # Query the database for matching documents
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/collection.html#pymongo.asynchronous.collection.AsyncCollection.find
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/asynchronous/cursor.html#pymongo.asynchronous.cursor.AsyncCursor
        cursor = collection.find(**query)
        documents = await cursor.to_list(query.get('limit'))
        if documents:
            response.update(count = len(documents))
            response.update(result = documents)
        if self.settings.get('debug', False):
            response.update(database = collection.database.name)
            response.update(collection = collection.name)
            response.update(query = query)
        # Normalize the response into a JSON formatted response
        self.set_header("Server", "Python/Tornado/MongoClient")
        self.set_header('Content-Type', 'text/json')
        response = json.dumps(response,
            indent=4,
            separators=(',', ': '),
            sort_keys=True,
            cls=ExtendedJSONEncoder,
            )
        self.write(response + '\n')
