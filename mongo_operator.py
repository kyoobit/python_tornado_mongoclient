import logging

from datetime import datetime, timezone
from urllib.parse import unquote_plus


def operator_value(field: str, value: str):
    """Expand operator string values"""

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
            gte, lte = v.split(",")
            return field, {
                "$gte": datetime.fromisoformat(gte),
                "$lte": datetime.fromisoformat(lte),
            }
        ## Comparison operators
        case "$lte":
            # https://docs.mongodb.com/manual/reference/operator/query/lte/
            return field, {"$lte": value}
        case "$eq":
            # https://docs.mongodb.com/manual/reference/operator/query/eq/
            return field, {"$eq": value}
        case "$gt":
            # https://docs.mongodb.com/manual/reference/operator/query/gt/
            return field, {"$gt": value}
        case "$gte":
            # https://docs.mongodb.com/manual/reference/operator/query/gte/
            return field, {"$gte": value}
        case "$in":
            # https://docs.mongodb.com/manual/reference/operator/query/in/
            return field, {"$in": value.split(",")}
        case "$lt":
            # https://docs.mongodb.com/manual/reference/operator/query/lt/
            return field, {"$lt": value}
        case "$lte":
            # https://docs.mongodb.com/manual/reference/operator/query/lte/
            return field, {"$lte": value}
        case "$ne":
            # https://docs.mongodb.com/manual/reference/operator/query/ne/
            return field, {"$ne": value}
        case "$nin":
            # https://docs.mongodb.com/manual/reference/operator/query/nin/
            return field, {"$nin": value.split(",")}
        ## Logical operators
        case "$and" | "$only":
            # https://docs.mongodb.com/manual/reference/operator/query/and/
            return "$and", [{field: word} for word in value.split(",")]
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
        ## Element operators
        case "$exists":
            # https://docs.mongodb.com/manual/reference/operator/query/exists/
            return field, {"$exists": value}
        #'$type'
        # Evaluation operators
        #'$expr'
        #'$jsonSchema'
        #'$mod'
        case "$regex":
            # https://docs.mongodb.com/manual/reference/operator/query/regex/
            return field, {"$regex": value, "$options": "i"}
        case "$text" | "$search":
            # https://docs.mongodb.com/manual/reference/operator/query/text/
            return "$text", {"$search": unquote_plus(value)}
        #'$where'
        # Geospatial operators
        #'$geoIntersects'
        #'$geoWithin'
        #'$near'
        #'$nearSphere'
        # Array operators
        #'$all'
        #'$elemMatch'
        #'$size'
        # Bitwise operators
        #'$bitsAllClear'
        #'$bitsAllSet'
        #'$bitsAnyClear'
        #'$bitsAnySet'
        # Comments operators
        #'$comment'
        # Projection operators
        #'$'
        #'$elemMatch'
        #'$meta'
        #'$slice'
        case _:
            logging.warning(f"Case not matched for: {operator!r}")

    return field, value
