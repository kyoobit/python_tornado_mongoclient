import json

from unittest.mock import AsyncMock, MagicMock

# https://pymongo.readthedocs.io/en/stable/
from pymongo.results import DeleteResult

# https://www.tornadoweb.org/en/stable/
import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestDeleteOneHandler_wo_Admin(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock DeleteResult instance
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.DeleteResult
        deleteresult = DeleteResult("mock_raw_result", True)

        # Mock collection delete_one method to return UpdateResult instance
        mock_collection.delete_one = AsyncMock(return_value=deleteresult)

        return make_app(debug=True, mock_collection=mock_collection)

    def test_delete_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/delete_one", {"method": "GET"}, 204),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestDeleteOneHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock DeleteResult instance
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.DeleteResult
        deleteresult = DeleteResult("mock_raw_result", True)

        # Mock collection delete_one method to return UpdateResult instance
        mock_collection.delete_one = AsyncMock(return_value=deleteresult)

        return make_app(debug=True, mock_collection=mock_collection, admin=True)

    def test_delete_one_wo_objectid(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/delete_one", {"method": "GET"}, 400),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)

    def test_delete_one_invalid_objectid(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/delete_one?_id=invalidid", {"method": "GET"}, 400),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)

    def test_delete_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            (
                "/delete_one?_id=abcdef0123456789abcdef01",
                {"method": "GET"},
                200,
            ),
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
            self.assertEqual(
                response_json["document"]["filter"]["_id"], "abcdef0123456789abcdef01"
            )
            self.assertIsInstance(response_json["result"][0], dict)
