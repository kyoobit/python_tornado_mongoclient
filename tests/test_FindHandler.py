import json

from unittest.mock import AsyncMock, MagicMock

# https://www.tornadoweb.org/en/stable/
import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestFindHandler(tornado.testing.AsyncHTTPTestCase):

    def get_app(self):
        # Mock database instance
        mock_database = MagicMock()
        mock_database.name = "mock_collection"

        # Mock collection instance
        mock_collection = MagicMock()
        mock_collection.database = mock_database
        mock_collection.name = "mock_collection"

        # Mock cursor instance
        mock_cursor = MagicMock()
        mock_cursor.name = "mock_cursor"
        mock_cursor.to_list = AsyncMock(return_value=[{"_id": "mock_document"}])

        # Mock collection find method to return a cursor
        mock_collection.find = MagicMock(return_value=mock_cursor)

        return make_app(debug=True, mock_collection=mock_collection)

    def test_find_one(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/find_one", {"method": "GET"}, 200),
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
            self.assertEqual(response_json.get("query"), {"filter": {}, "limit": 1})
            self.assertIsInstance(response_json.get("result"), list)

    def test_find(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/find", {"method": "GET"}, 200),
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
            self.assertEqual(response_json.get("query"), {"filter": {}, "limit": 10})
            self.assertIsInstance(response_json.get("result"), list)

    def test_query_limit(self):
        for path, options, status_code, expected in [
            # REQUEST: (path:str, options:dict, status_code:int, expected)
            ("/find", {"method": "GET"}, 200, 10),
            ("/find_one", {"method": "GET"}, 200, 1),
            ("/find_one?limit=11", {"method": "GET"}, 200, 1),
            ("/find?limit=9", {"method": "GET"}, 200, 9),
            ("/find?limit=99", {"method": "GET"}, 200, 99),
            ("/find?limit=0", {"method": "GET"}, 200, 10),
            ("/find?limit=-1", {"method": "GET"}, 200, 10),
            ("/find?limit=ten", {"method": "GET"}, 400, "-"),
            ("/find?limit=", {"method": "GET"}, 400, "-"),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            if expected != "-":
                # The response body must be in valid JSON format
                response_json = json.loads(response.body)
                print(f"response_json: {response_json!r}")
                # Check response JSON for expected values
                self.assertEqual(response_json["query"].get("limit"), expected)

    def test_query_projection(self):
        for path, options, status_code, expected in [
            # REQUEST: (path:str, options:dict, status_code:int, expected)
            ("/find", {"method": "GET"}, 200, None),
            ("/find?projection=key", {"method": "GET"}, 200, ["key"]),
            ("/find?projection=a,b,c", {"method": "GET"}, 200, ["a", "b", "c"]),
            ("/find?projection=", {"method": "GET"}, 200, None),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            if expected != "-":
                # The response body must be in valid JSON format
                response_json = json.loads(response.body)
                print(f"response_json: {response_json!r}")
                # Check response JSON for expected values
                self.assertEqual(response_json["query"].get("projection"), expected)

    def test_query_skip(self):
        for path, options, status_code, expected in [
            # REQUEST: (path:str, options:dict, status_code:int, expected)
            ("/find", {"method": "GET"}, 200, None),
            ("/find?skip=0", {"method": "GET"}, 200, 0),
            ("/find?skip=3", {"method": "GET"}, 200, 3),
            ("/find?skip=-3", {"method": "GET"}, 200, 0),
            ("/find?skip=three", {"method": "GET"}, 400, "-"),
            ("/find?skip=", {"method": "GET"}, 400, "-"),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            if expected != "-":
                # The response body must be in valid JSON format
                response_json = json.loads(response.body)
                print(f"response_json: {response_json!r}")
                # Check response JSON for expected values
                self.assertEqual(response_json["query"].get("skip"), expected)

    def test_query_sort(self):
        for path, options, status_code, expected in [
            # REQUEST: (path:str, options:dict, status_code:int, expected)
            ("/find", {"method": "GET"}, 200, None),
            ("/find?sort=key", {"method": "GET"}, 200, [["key", 1]]),
            ("/find?sort=-key", {"method": "GET"}, 200, [["key", -1]]),
            ("/find?sort=", {"method": "GET"}, 200, None),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            if expected != "-":
                # The response body must be in valid JSON format
                response_json = json.loads(response.body)
                print(f"response_json: {response_json!r}")
                # Check response JSON for expected values
                self.assertEqual(response_json["query"].get("sort"), expected)
