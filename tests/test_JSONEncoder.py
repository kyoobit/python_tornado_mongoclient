import unittest

from datetime import datetime, timezone

import pytest

import tornado

from mongo_jsonencoder import ExtendedJSONEncoder


# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestJSONEncoder(unittest.TestCase):

    def test_encoding_bytes(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default("value".encode())
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(value, "value")

    def test_encoding_datetime(self):
        encoder = ExtendedJSONEncoder()
        dt = datetime.now(tz=timezone.utc)
        dt = dt.replace(microsecond=0)
        value = encoder.default(dt)
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(dt, datetime.fromisoformat(value))

    def test_encoding_NotImplementedError(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(NotImplementedError("value"))
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(value, "value")

    def test_encoding_ValueError(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(ValueError("value"))
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(value, "value")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_pymongo_results_DeleteResult(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_pymongo_results_InsertOneResult(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_bson_errors_InvalidId(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_bson_objectid_ObjectId(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_ppymongo_errors_OperationFailure(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_bson_timestamp_Timestamp(self):
        raise NotImplementedError("...work to do!")

    @pytest.mark.skip(reason="Not implemented yet")
    def test_pymongo_results_UpdateResult(self):
        raise NotImplementedError("...work to do!")

    def test_tornado_httpclient_HTTPClientError(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(tornado.httpclient.HTTPClientError(600))
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(value, {"code": 600, "reason": "-"})

    def test_tornado_httpclient_HTTPRequest(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(tornado.httpclient.HTTPRequest("/"))
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertIsInstance(value, dict)

    def test_tornado_httpclient_HTTPResponse(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(
            tornado.httpclient.HTTPResponse(tornado.httpclient.HTTPRequest("/"), 600)
        )
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertIsInstance(value, dict)

    def test_tornado_httputil_HTTPHeaders(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(tornado.httputil.HTTPHeaders())
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertIsInstance(value, dict)

    def test_tornado_httputil_HTTPServerRequest(self):
        encoder = ExtendedJSONEncoder()
        value = encoder.default(tornado.httputil.HTTPServerRequest())
        print(f"value: {value!r}")
        # Check the query values for expected values
        self.assertIsInstance(value, dict)

    @pytest.mark.skip(reason="Not implemented yet")
    def test_tornado_web_StaticFileHandler(self):
        raise NotImplementedError("...work to do!")
