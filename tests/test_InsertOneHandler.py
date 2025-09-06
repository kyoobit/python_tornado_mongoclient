import json

from unittest.mock import AsyncMock, MagicMock

# https://pymongo.readthedocs.io/en/stable/
from pymongo.results import InsertOneResult

# https://www.tornadoweb.org/en/stable/
import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestInsertOneHandler_wo_Admin(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock InsertOneResult instance
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.InsertOneResult
        insertoneresult = InsertOneResult("mock_document_id", True)

        # Mock collection find method to return a cursor
        mock_collection.insert_one = AsyncMock(return_value=insertoneresult)

        return make_app(debug=True, mock_collection=mock_collection)

    def test_insert_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/insert_one", {"method": "GET"}, 204),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestInsertOneHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock InsertOneResult
        insertoneresult = MagicMock()
        insertoneresult.inserted_id = "mock_document_id"
        insertoneresult.acknowledged = True

        # Mock collection find method to return a cursor
        mock_collection.insert_one = AsyncMock(return_value=insertoneresult)

        return make_app(debug=True, mock_collection=mock_collection, admin=True)

    def test_insert_one_wo_arguments(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/insert_one", {"method": "GET"}, 200),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            # The response body must be in valid JSON format
            response_json = json.loads(response.body)
            print(f"response_json: {response_json!r}")
            # Check response JSON for expected values
            self.assertEqual(response_json.get("count"), 1)
            self.assertIsNotNone(response_json["document"]["ctime"])
            self.assertIsNotNone(response_json["document"]["mtime"])
            self.assertIsInstance(response_json["result"], list)

    def test_insert_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/insert_one?key=value", {"method": "GET"}, 200),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            # The response body must be in valid JSON format
            response_json = json.loads(response.body)
            print(f"response_json: {response_json!r}")
            # Check response JSON for expected values
            self.assertEqual(response_json.get("count"), 1)
            self.assertIsNotNone(response_json["document"]["ctime"])
            self.assertIsNotNone(response_json["document"]["mtime"])
            self.assertEqual(response_json["document"]["key"], "value")
            self.assertIsInstance(response_json["result"], list)
