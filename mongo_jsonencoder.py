import datetime
import json

# https://pymongo.readthedocs.io/en/stable/
import bson.errors
import bson.objectid
import bson.timestamp
import pymongo.errors
import pymongo.results

# https://www.tornadoweb.org/en/stable/
import tornado.httpclient
import tornado.httputil
import tornado.web


class ExtendedJSONEncoder(json.JSONEncoder):
    """Extend the JSONEncoder to handle additional data types.

    Example usage:
      json.dumps(result, indent=4, separators=(',', ': '),
        sort_keys=True, cls=ExtendedJSONEncoder)
    """

    def default(self, obj, *args, **kwargs):
        try:
            match obj:
                # Python native types
                case bytes():
                    # Decode `bytes' instances with a reasonable limit
                    return obj.decode("utf-8", "replace")[:120]
                case datetime.datetime():
                    # Return datetime instances in ISO format
                    # https://docs.python.org/3/library/datetime.html#datetime.datetime.isoformat
                    return obj.isoformat(timespec="seconds")
                case NotImplementedError() | ValueError():
                    # Handle *Some* Python Exception Classes
                    # https://docs.python.org/3/library/exceptions.html
                    return str(obj)
                case type():
                    return str(obj)
                case pymongo.results.DeleteResult():
                    # pymongo.results.DeleteResult
                    # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.DeleteResult
                    return {
                        "acknowledged": getattr(obj, "acknowledged", "-"),
                        "deleted_count": getattr(obj, "deleted_count", "-"),
                        "raw_result": getattr(obj, "raw_result", "-"),
                    }
                case pymongo.results.InsertOneResult():
                    # pymongo.results.InsertOneResult
                    # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.InsertOneResult
                    return {
                        "acknowledged": getattr(obj, "acknowledged", "-"),
                        "inserted_id": getattr(obj, "inserted_id", "-"),
                    }
                case bson.errors.InvalidId():
                    # bson.errors.InvalidId
                    # https://pymongo.readthedocs.io/en/stable/api/bson/errors.html
                    return {
                        "code": getattr(obj, "code", "-"),
                        "details": getattr(obj, "args", ["-"])[0],
                    }
                case bson.objectid.ObjectId():
                    # bson.objectid.ObjectId
                    # https://pymongo.readthedocs.io/en/stable/api/bson/objectid.html
                    return str(obj)
                case pymongo.errors.OperationFailure():
                    # pymongo.errors.OperationFailure
                    # https://pymongo.readthedocs.io/en/stable/api/pymongo/errors.html#pymongo.errors.OperationFailure
                    return {
                        "code": getattr(obj, "code", "-"),
                        "details": getattr(obj, "details", "-"),
                    }
                case bson.timestamp.Timestamp():
                    # bson.timestamp.Timestamp
                    # https://pymongo.readthedocs.io/en/stable/api/bson/timestamp.html
                    return obj.as_datetime()
                case pymongo.results.UpdateResult():
                    # pymongo.results.UpdateResult
                    # https://pymongo.readthedocs.io/en/stable/api/pymongo/results.html#pymongo.results.UpdateResult
                    return {
                        "acknowledged": getattr(obj, "acknowledged", "-"),
                        "matched_count": getattr(obj, "matched_count", "-"),
                        "modified_count": getattr(obj, "modified_count", "-"),
                        "raw_result": getattr(obj, "raw_result", "-"),
                        "upserted_id": getattr(obj, "upserted_id", "-"),
                    }
                # TornadoWeb types
                # -------------------------------------------------------------
                case tornado.httpclient.HTTPClientError():
                    # https://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.HTTPClientError
                    return {
                        "code": getattr(obj, "code", "-"),
                        "reason": getattr(obj, "reason", "-"),
                    }
                case tornado.httpclient.HTTPRequest():
                    # https://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.HTTPRequest
                    # https://www.tornadoweb.org/en/stable/httputil.html#tornado.httputil.HTTPHeaders
                    return {
                        "headers": getattr(obj, "headers", "-"),
                        "method": getattr(obj, "method", "-"),
                        "url": getattr(obj, "url", "-"),
                        "validate_cert": getattr(obj, "validate_cert", "-"),
                    }
                case tornado.httpclient.HTTPResponse():
                    # https://www.tornadoweb.org/en/stable/httpclient.html#tornado.httpclient.HTTPResponse
                    # https://www.tornadoweb.org/en/stable/httputil.html#tornado.httputil.HTTPHeaders
                    headers = {}
                    for field_name, field_value in sorted(obj.headers.get_all()):
                        headers[field_name] = field_value
                    return {
                        "code": getattr(obj, "code", "-"),
                        "effective_url": getattr(obj, "effective_url", "-"),
                        "error": getattr(obj, "error", "-"),
                        "headers": headers,
                        "reason": getattr(obj, "reason", "-"),
                        "body_length": len(getattr(obj, "body", "")),
                    }
                case tornado.httputil.HTTPHeaders():
                    # https://www.tornadoweb.org/en/stable/httputil.html#tornado.httputil.HTTPHeaders
                    headers = {}
                    for field_name, field_value in sorted(obj.get_all()):
                        headers[field_name] = field_value
                    return headers
                case tornado.httputil.HTTPServerRequest():
                    # https://www.tornadoweb.org/en/stable/httputil.html#tornado.httputil.HTTPServerRequest
                    headers = {}
                    for field_name, field_value in sorted(obj.headers.get_all()):
                        headers[field_name] = field_value
                    return {
                        "method": getattr(obj, "method", "-"),
                        "version": getattr(obj, "version", "-"),
                        "headers": headers,
                        "host": getattr(obj, "host", "-"),
                    }
                case tornado.web.StaticFileHandler():
                    # https://www.tornadoweb.org/en/stable/web.html#tornado.web.StaticFileHandler
                    return "<StaticFileHandler()>"
                # default
                case _:
                    return super().default(obj)
        except TypeError:
            return str(type(obj)).replace("'", "")
        except Exception as error:
            print("ExtendedJSONEncoder - Failed to convert obj")
            print(f"{type(obj)}: {error!r}")
            return str(type(obj)).replace("'", "")
