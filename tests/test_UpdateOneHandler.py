import json

from unittest.mock import AsyncMock, MagicMock

# https://pymongo.readthedocs.io/en/stable/
from pymongo.results import UpdateResult

# https://www.tornadoweb.org/en/stable/
import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestUpdateOneHandler_wo_Admin(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock UpdateResult instance
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.UpdateResult
        updateresult = UpdateResult("mock_raw_result", True)

        # Mock collection update_one method to return UpdateResult instance
        mock_collection.update_one = AsyncMock(return_value=updateresult)

        return make_app(debug=True, mock_collection=mock_collection)

    def test_update_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/update_one", {"method": "GET"}, 204),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestUpdateOneHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock UpdateResult instance
        # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.UpdateResult
        updateresult = UpdateResult("mock_raw_result", True)

        # Mock collection update_one method to return UpdateResult instance
        mock_collection.update_one = AsyncMock(return_value=updateresult)

        return make_app(debug=True, mock_collection=mock_collection, admin=True)

    def test_update_one_wo_objectid(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/update_one", {"method": "GET"}, 400),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)

    def test_update_one_invalid_objectid(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/update_one?_id=invalidid", {"method": "GET"}, 400),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)

    def test_update_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            (
                "/update_one?_id=abcdef0123456789abcdef01&key=value",
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
            self.assertIsNotNone(response_json["document"]["update"]["$set"]["mtime"])
            self.assertEqual(
                response_json["document"]["update"]["$set"]["key"], "value"
            )
            self.assertIsInstance(response_json["result"][0], dict)

    def test_update_one_nothing_to_do(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            (
                "/update_one?_id=abcdef0123456789abcdef01",
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
            self.assertIsNotNone(response_json["document"]["update"]["$set"]["mtime"])
            self.assertIsInstance(response_json["result"][0], dict)

    def test_update_one_bad_objectid(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            (
                "/update_one?_id=bad_objectid",
                {"method": "GET"},
                400,
            ),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
