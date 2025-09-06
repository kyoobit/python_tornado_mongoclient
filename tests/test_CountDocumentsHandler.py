import json

from unittest.mock import MagicMock

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

        # Mock collection find method to return a cursor
        mock_collection.count_documents = MagicMock(return_value=999)

        return make_app(debug=True, mock_collection=mock_collection)

    def test_count_documents(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/count_documents", {"method": "GET"}, 200),
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
            self.assertEqual(response_json.get("count"), 999)
            self.assertEqual(response_json.get("query"), {"filter": {}})
            self.assertIsInstance(response_json.get("result"), list)

    def test_count_documents_w_filter(self):
        for path, options, status_code in [
            # REQUEST: (path:str, options:dict, status_code:int)
            ("/count_documents?status=$in:public", {"method": "GET"}, 200),
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
            self.assertEqual(response_json.get("count"), 999)
            self.assertEqual(
                response_json.get("query"), {"filter": {"status": {"$in": ["public"]}}}
            )
            self.assertIsInstance(response_json.get("result"), list)
