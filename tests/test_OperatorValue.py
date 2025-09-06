import datetime
import unittest

# https://pymongo.readthedocs.io/en/stable/
from bson.objectid import ObjectId
from bson.errors import InvalidId

import pytest

from mongo_operator import operator_value


# https://docs.python.org/3/library/unittest.html#unittest.TestCase
class TestOperatorValue(unittest.TestCase):

    def test_objectid(self):
        field, value = operator_value("_id", "abcdef0123456789abcdef01")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "_id")
        self.assertIsInstance(value, ObjectId)

    def test_objectid_none(self):
        field, value = operator_value("_id", None)
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "_id")
        self.assertIsNone(value)

    def test_objectid_error(self):
        # https://pymongo.readthedocs.io/en/stable/api/bson/errors.html#bson.errors.InvalidId
        with pytest.raises(InvalidId):
            field, value = operator_value("_id", "an invalid _id")

    def test_bool_true(self):
        field, value = operator_value("field", "true")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertEqual(value, True)

    def test_bool_false(self):
        field, value = operator_value("field", "false")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertEqual(value, False)

    def test_not_a_str(self):
        field, value = operator_value("field", None)
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertEqual(value, None)

    def test_not_an_operator(self):
        field, value = operator_value("field", "value")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertEqual(value, "value")

    def test_unknown_operator(self):
        field, value = operator_value("field", "$unknown:value")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertEqual(value, "value")

    def test_datetime_now(self):
        field, value = operator_value("field", "$test:$now")
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertIsInstance(value, datetime.datetime)

    def test_operator_between(self):
        field, value = operator_value(
            "field", "$between:2025-08-01T00:00,2025-08-31T23:59"
        )
        print(f"field: {field!r}, value: {value!r}")
        # Check the query values for expected values
        self.assertEqual(field, "field")
        self.assertIsInstance(value, dict)
        self.assertIsInstance(value["$gte"], datetime.datetime)
        self.assertIsInstance(value["$lte"], datetime.datetime)

    def test_comparison_operators(self):
        for operator in [
            "$lte",
            "$eq",
            "$gt",
            "$gte",
            "$lt",
            "$lte",
            "$ne",
        ]:
            field, value = operator_value("field", f"{operator}:value")
            print(f"field: {field!r}, value: {value!r}")
            self.assertEqual(field, "field")
            self.assertEqual(value, {operator: "value"})

    def test_logical_operators(self):
        for operator in [
            "$and",
            "$only",
            "$nor",
            "$or",
            "$any",
        ]:
            field, value = operator_value("field", f"{operator}:value")
            print(f"field: {field!r}, value: {value!r}")
            if operator == "$only":
                self.assertEqual(field, "$and")
            elif operator == "$any":
                self.assertEqual(field, "$or")
            else:
                self.assertEqual(field, operator)
            self.assertEqual(value, [{"field": "value"}])

    def test_logical_operator_not(self):
        field, value = operator_value("field", "$not:operator:expression")
        print(f"field: {field!r}, value: {value!r}")
        self.assertEqual(field, "field")
        self.assertEqual(value, {"$not": {"operator": "expression"}})

    def test_logical_operator_in_nin(self):
        for operator in [
            "$in",
            "$nin",
        ]:
            field, value = operator_value("field", f"{operator}:value")
            print(f"field: {field!r}, value: {value!r}")
            self.assertEqual(field, "field")
            self.assertEqual(value, {operator: ["value"]})

    def test_element_operator_exists(self):
        field, value = operator_value("field", "$exists:value")
        print(f"field: {field!r}, value: {value!r}")
        self.assertEqual(field, "field")
        self.assertEqual(value, {"$exists": "value"})

    def test_evaluation_operator_regex(self):
        field, value = operator_value("field", "$regex:value")
        print(f"field: {field!r}, value: {value!r}")
        self.assertEqual(field, "field")
        self.assertEqual(value, {"$regex": "value", "$options": "i"})

    def test_evaluation_operator_text(self):
        for operator in [
            "$text",
            "$search",
        ]:
            field, value = operator_value("field", f"{operator}:some+value")
            print(f"field: {field!r}, value: {value!r}")
            self.assertEqual(field, "$text")
            self.assertEqual(value, {"$search": "some value"})
