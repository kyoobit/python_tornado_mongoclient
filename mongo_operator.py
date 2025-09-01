import logging

from datetime import datetime, timezone


def operator_value(field:str, value:str):
    """Expand operator string values"""

    # Catch and exit when not an unprocessed operator
    if not isinstance(value, str) or not value.startswith('$'):
        return field, value

    # Split the operator from the string value
    operator, value = value.split(':', 1)

    # Match the value expansion format
    match value:
        case '$now':
            # Set the value to current UTC date/time
            value = datetime.now(tz=timezone.utc)
        case _:
            pass

    # Match the operator expansion format
    match operator:
        case '$and':
            # https://docs.mongodb.com/manual/reference/operator/query/and/
            return '$and', [{field: word} for word in value.split(',')]
        case '$in':
            # https://docs.mongodb.com/manual/reference/operator/query/in/
            return field, {'$in': value.split(',')}
        case '$lte':
            # https://docs.mongodb.com/manual/reference/operator/query/lte/
            return field, {'$lte': value}
        case _:
            logging.warning(f"Case not matched for: {operator!r}")

    return field, value
