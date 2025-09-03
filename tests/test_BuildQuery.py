import unittest

from unittest.mock import MagicMock

from mongo_query import build_query


# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestBuildQuery(unittest.TestCase):

    def test_defaults(self):
        # Input setup
        settings = {}
        request = MagicMock()
        request.arguments = {}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query, {"limit": 1, "filter": {}})

    def test_filter_bool_no_default(self):
        settings = {"default_query_filter": {}}
        request = MagicMock()
        request.arguments = {"key": [b"true"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": True})

    def test_filter_bool_no_argument(self):
        settings = {"default_query_filter": {"key": False}}
        request = MagicMock()
        request.arguments = {}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": False})

    def test_filter_bool_override(self):
        settings = {"default_query_filter": {"key": False}}
        request = MagicMock()
        request.arguments = {"key": [b"true"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": False})

    def test_filter_dict_no_default(self):
        settings = {"default_query_filter": {}}
        request = MagicMock()
        request.arguments = {"key": [b"$in:argument"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": {"$in": ["argument"]}})

    def test_filter_dict_no_argument(self):
        settings = {"default_query_filter": {"key": {"$nin": ["default"]}}}
        request = MagicMock()
        request.arguments = {}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": {"$nin": ["default"]}})

    def test_filter_dict_merge(self):
        settings = {"default_query_filter": {"key": {"$nin": ["default"]}}}
        request = MagicMock()
        request.arguments = {"key": [b"$in:argument"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(
            query["filter"], {"key": {"$in": ["argument"], "$nin": ["default"]}}
        )

    def test_filter_dict_override(self):
        settings = {"default_query_filter": {"key": {"$nin": ["default"]}}}
        request = MagicMock()
        request.arguments = {"key": [b"$nin:argument"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": {"$nin": ["default"]}})

    def test_filter_str_no_default(self):
        settings = {"default_query_filter": {}}
        request = MagicMock()
        request.arguments = {"key": [b"argument"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": "argument"})

    def test_filter_str_no_argument(self):
        settings = {"default_query_filter": {"key": "default"}}
        request = MagicMock()
        request.arguments = {}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": "default"})

    def test_filter_str_override(self):
        settings = {"default_query_filter": {"key": "default"}}
        request = MagicMock()
        request.arguments = {"key": [b"argument"]}
        # Build the query using the inputs
        query = build_query(settings, request)
        print(f"query: {query!r}")
        # Check the query values for expected values
        self.assertEqual(query["filter"], {"key": "default"})
