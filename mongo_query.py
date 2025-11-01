import copy
import logging

from pathlib import Path

from mongo_operator import operator_value


def build_query(settings, request):
    """Build the query filter document and query options"""
    prefix = f"{Path(__file__).name} - build_query()"  # log message prefix

    # Unpack and parse the request arguments
    arguments = {}
    for key, value in request.arguments.items():
        # Unpack the value [..., b'value'] ---> 'value'
        value = value[-1].decode()
        # Process operators 'field=$foo:bar' ---> 'field', {'$foo': ['bar']}
        key, value = operator_value(key, value)
        arguments[key] = value
    logging.debug(f"{prefix} - arguments: {arguments!r}")

    # Remove known query option key/values from the arguments
    query = copy.deepcopy(settings.get("default_query_options", {}))
    for key in ["limit", "projection", "skip", "sort"]:
        if key in arguments.keys():
            value = arguments.pop(key)
            # Do not pass on empty values
            if value != "":
                query[key] = value
    logging.debug(f"{prefix} - query: {query!r}")

    # Handle (re)setting specific query options
    query = set_option_limit(request, query)
    query = set_option_projection(request, query)
    query = set_option_skip(request, query)
    query = set_option_sort(request, query)
    logging.debug(f"{prefix} - query: {query!r}")

    # Merge the arguments and default query filter
    # The default values may override request arguments
    # Evaluate the combined set of keys from default and request arguments
    query_filter = {}
    default_query_filter = settings.get("default_query_filter", {})
    for key in set(list(default_query_filter.keys()) + list(arguments.keys())):
        # Get the expanded value for the key from the default_query_filter
        # 'field=$foo:bar' ---> 'field', {'$foo': ['bar']}
        key, value = operator_value(key, default_query_filter.get(key))
        logging.debug(f"{prefix} - key: {key!r} is: {value!r} in default_query_filter")
        logging.debug(
            f"{prefix} - key: {key!r} is: {arguments.get(key)!r} in arguments"
        )

        # Key does exist in arguments and default value is None
        if value is None and arguments.get(key) is not None:
            logging.debug(
                f"{prefix} - setting: {key!r} to: {arguments.get(key)!r}, None in query_filter"
            )
            query_filter[key] = arguments.get(key)

        # Key does NOT exist in arguments and default value is NOT None
        elif key not in arguments.keys() and value is not None:
            logging.debug(f"{prefix} - setting: {key!r} to: {value!r} in query_filter")
            query_filter[key] = value

        # Key exists and both values are dictionaries
        # Keys in the default value are preferred when keys overlap
        elif isinstance(arguments.get(key), dict) and isinstance(value, dict):
            merged_value = {**arguments.get(key), **value}
            logging.debug(
                f"{prefix} - merged: {key!r} as: {merged_value!r} in query_filter"
            )
            query_filter[key] = merged_value

        # Key does exist in arguments
        # Overwrite with the default value
        else:
            logging.debug(
                f"{prefix} - overwriting: {key!r} to: {value!r} in query_filter"
            )
            query_filter[key] = value

    # Add the query_filter as filter to the query
    query.update(filter=query_filter)

    logging.debug(f"{prefix} - query: {query!r}")
    return query


def set_option_limit(request, query: dict) -> dict:
    """Enforce query result limit"""
    prefix = f"{Path(__file__).name} - set_option_limit()"  # log message prefix

    if request.path.endswith("_one"):
        query.update(limit=1)

    # Allow a limit to be specified by a request argument of 'limit'
    elif request.arguments.get("limit") is not None:
        limit = int(request.arguments.get("limit")[-1])
        # Enforce a positive int
        if limit >= 1:
            query.update(limit=limit)
        # Apply a default when zero or less
        else:
            query.update(limit=10)

    # Always set a default when a value is not set
    if query.get("limit") is None:
        query.update(limit=10)

    logging.debug(f"{prefix} - query['limit']: {query.get('limit')!r}")
    return query


def set_option_projection(request, query) -> dict:
    prefix = f"{Path(__file__).name} - set_option_projection()"  # log message prefix

    # Allow a projection to be specified by a request argument of 'projection'
    # Only when a projection was not already set by default_query_options
    if request.arguments.get("projection") is not None:
        projection = request.arguments.get("projection")[-1].decode()
        if projection != "":
            projection = projection.split(",")
            query.update(projection=projection)

    logging.debug(f"{prefix} - query['projection']: {query.get('projection')!r}")
    return query


def set_option_skip(request, query) -> dict:
    prefix = f"{Path(__file__).name} - set_option_skip()"  # log message prefix

    # Allow skip to be specified by a request argument of 'skip'
    if request.arguments.get("skip") is not None:
        skip = int(request.arguments.get("skip")[-1])
        if skip >= 1:
            query.update(skip=skip)
        else:
            query.update(skip=0)

    logging.debug(f"{prefix} - query['skip']: {query.get('skip')!r}")
    return query


def set_option_sort(request, query) -> dict:
    prefix = f"{Path(__file__).name} - set_option_sort()"  # log message prefix

    # Allow sort to be specified by a request argument key of 'sort'
    if request.arguments.get("sort") is not None:
        sort = request.arguments.get("sort")[-1].decode()
        if sort:
            if sort.startswith("-"):
                # pymongo.DESCENDING = -1 Descending sort order.
                sort = [(sort[1:], -1)]  # descending
            else:
                # pymongo.ASCENDING = 1 Ascending sort order.
                sort = [(sort, 1)]  # ascending
            query.update(sort=sort)

    logging.debug(f"{prefix} - query['sort']: {query.get('sort')!r}")
    return query
