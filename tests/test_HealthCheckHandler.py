from unittest.mock import AsyncMock, MagicMock

import pytest

# https://www.tornadoweb.org/en/stable/
import tornado

from app import make_app


# https://www.tornadoweb.org/en/stable/testing.html
# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestHealthCheckHandler(tornado.testing.AsyncHTTPTestCase):

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

        # Mock collection find_one method to return a cursor
        mock_collection.find_one = MagicMock(return_value=mock_cursor)

        return make_app(mock_collection=mock_collection)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_healthcheck(self):
        raise NotImplementedError("...work to do")
