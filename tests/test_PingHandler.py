import tornado

from app import make_app


class TestPingHandler(tornado.testing.AsyncHTTPTestCase):
    def get_app(self):
        return make_app()

    def test_ping(self):
        for path, options, status_code in [
            # REQUEST: tuple = (path: str, options: dict, status_code: int),
            ("/ping", {"method": "GET"}, 200),
        ]:
            print(f"path: {path!r}, options: {options!r}")
            # Make the HTTP request
            response = self.fetch(f"{path}", **options)
            # Check response code for the expected value
            self.assertEqual(response.code, status_code)
            # Check response body for expected values
            if status_code == 200:
                self.assertEqual(response.body, b'{"ping": "pong"}')
