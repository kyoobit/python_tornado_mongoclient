import tornado

from app import make_app


class TestDefaultHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_requests(self):
        for path, options, status_code in [
            # REQUEST: tuple = (path: str, options: dict, status_code: int),
            ("/", {"method": "GET"}, 204),
            ("/foo", {"method": "GET"}, 204),
            ("/bar", {"method": "GET"}, 204),
            ("/", {"method": "HEAD"}, 405),
            ("/", {"method": "OPTIONS"}, 405),
            ("/", {"method": "DELETE"}, 405),
            ("/", {"method": "POST", "body": b'{"test": true}'}, 405),
            ("/", {"method": "PUT", "body": b'{"test": true}'}, 405),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
