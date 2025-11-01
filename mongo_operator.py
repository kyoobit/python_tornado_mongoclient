import logging

from datetime import datetime, timezone
from urllib.parse import unquote_plus

# https://pymongo.readthedocs.io/en/stable/
from bson.objectid import ObjectId


def operator_value(field: str, value: str):
    """Expand operator string values"""

    # Catch nested field conversion
    if field.startswith("$nested:"):
        field = field.split(":", 1)[-1]
        field1, field2 = field.split(".", 1)
        field2, value = operator_value(field2, value)
        return field1, {field2: value}

    # Catch ObjectId conversion
    # https://pymongo.readthedocs.io/en/stable/api/bson/objectid.html#bson.objectid.ObjectId
    if field == "_id" and isinstance(value, str):
        return field, ObjectId(value)

    # Catch bool conversion
    if value == "true":
        return field, True
    elif value == "false":
        return field, False

    # Catch datetime conversion
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value)
            return field, value
        except ValueError:
            pass

    # Catch integer number conversion
    if isinstance(value, str) and value.isdigit():
        value = int(value)
        return field, value

    # Catch float number conversion
    if isinstance(value, str) and value.find(".") != -1:
        try:
            value = float(value)
            return field, value
        except ValueError:
            pass

    # Catch and exit when not an unprocessed operator
    if not isinstance(value, str) or not value.startswith("$"):
        return field, value

    # Split the operator from the string value
    operator, value = value.split(":", 1)

    # Match the value expansion format
    match value:
        case "$now":
            # Set the value to current UTC date/time
            value = datetime.now(tz=timezone.utc)
        case _:
            pass

    # Match the operator expansion format
    match operator:
        # Non-standard operators
        case "$between":
            # sugar for creating a `$gte+$lte' filter
            gte, lte = value.split(",")
            return field, {
                "$gte": datetime.fromisoformat(gte),
                "$lte": datetime.fromisoformat(lte),
            }
        case "$list":
            # parse the value as a comma separated list
            return field, value.split(",")
        # Comparison operators
        case "$eq":
            # https://docs.mongodb.com/manual/reference/operator/query/eq/
            return field, {"$eq": value}
        case "$gt":
            # https://docs.mongodb.com/manual/reference/operator/query/gt/
            return field, {"$gt": value}
        case "$gte":
            # https://docs.mongodb.com/manual/reference/operator/query/gte/
            return field, {"$gte": value}
        case "$lt":
            # https://docs.mongodb.com/manual/reference/operator/query/lt/
            return field, {"$lt": value}
        case "$lte":
            # https://docs.mongodb.com/manual/reference/operator/query/lte/
            return field, {"$lte": value}
        case "$ne":
            # https://docs.mongodb.com/manual/reference/operator/query/ne/
            return field, {"$ne": value}
        # Logical operators
        case "$and" | "$only":
            # https://docs.mongodb.com/manual/reference/operator/query/and/
            return "$and", [{field: word} for word in value.split(",")]
        case "$in":
            # https://docs.mongodb.com/manual/reference/operator/query/in/
            return field, {"$in": value.split(",")}
        case "$nin":
            # https://docs.mongodb.com/manual/reference/operator/query/nin/
            return field, {"$nin": value.split(",")}
        case "$not":
            # https://docs.mongodb.com/manual/reference/operator/query/not/
            o, e = value.split(":", 1)
            return field, {"$not": {o: e}}
        case "$nor":
            # https://docs.mongodb.com/manual/reference/operator/query/nor/
            return "$nor", [{field: word} for word in value.split(",")]
        case "$or" | "$any":
            # https://docs.mongodb.com/manual/reference/operator/query/or/
            return "$or", [{field: word} for word in value.split(",")]
        # Element operators
        case "$exists":
            # https://docs.mongodb.com/manual/reference/operator/query/exists/
            return field, {"$exists": value}
        # case '$type'
        # Evaluation operators
        # case '$expr'
        # case '$jsonSchema'
        # case '$mod'
        case "$regex":
            # https://docs.mongodb.com/manual/reference/operator/query/regex/
            return field, {"$regex": value, "$options": "i"}
        case "$text" | "$search":
            # https://docs.mongodb.com/manual/reference/operator/query/text/
            return "$text", {"$search": unquote_plus(value)}
        # case '$where'
        # Geospatial operators
        # case '$geoIntersects'
        # case '$geoWithin'
        # case '$near'
        # case '$nearSphere'
        # Array operators
        # case '$all'
        # case '$elemMatch'
        # case '$size'
        # Bitwise operators
        # case '$bitsAllClear'
        # case '$bitsAllSet'
        # case '$bitsAnyClear'
        # case '$bitsAnySet'
        # Comments operators
        # case '$comment'
        # Projection operators
        # case '$'
        # case '$elemMatch'
        # case '$meta'
        # case '$slice'
        case _:
            logging.warning(f"Case not matched for: {operator!r}")

    return field, value
