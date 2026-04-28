"""Unit tests for ObjectListParser."""

from graphqler.compiler.parsers.object_list_parser import ObjectListParser


def test_parses_nested_wrapped_output_types_without_explicit_leaf_oftype_key():
    data = {
        "data": {
            "__schema": {
                "types": [
                    {
                        "kind": "OBJECT",
                        "name": "Project",
                        "fields": [
                            {
                                "name": "items",
                                "args": [],
                                "type": {
                                    "kind": "NON_NULL",
                                    "ofType": {
                                        "kind": "LIST",
                                        "ofType": {
                                            "kind": "OBJECT",
                                            "name": "Item",
                                        },
                                    },
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }

    result = ObjectListParser().parse(data)

    field = result["Project"]["fields"][0]
    assert field["kind"] == "NON_NULL"
    assert field["type"] is None
    assert field["ofType"] == {
        "kind": "LIST",
        "name": None,
        "ofType": {
            "kind": "OBJECT",
            "name": "Item",
            "ofType": None,
            "type": "Item",
        },
        "type": None,
    }


def test_parses_args_when_optional_introspection_keys_are_missing():
    data = {
        "data": {
            "__schema": {
                "types": [
                    {
                        "kind": "OBJECT",
                        "name": "Project",
                        "fields": [
                            {
                                "name": "item",
                                "args": [
                                    {
                                        "name": "id",
                                        "type": {
                                            "kind": "NON_NULL",
                                            "ofType": {
                                                "kind": "SCALAR",
                                                "name": "ID",
                                            },
                                        },
                                    }
                                ],
                                "type": {
                                    "kind": "OBJECT",
                                    "name": "Item",
                                },
                            }
                        ],
                    }
                ]
            }
        }
    }

    result = ObjectListParser().parse(data)

    arg = result["Project"]["fields"][0]["inputs"]["id"]
    assert arg["description"] is None
    assert arg["defaultValue"] is None
    assert arg["ofType"] == {
        "kind": "SCALAR",
        "name": "ID",
        "ofType": None,
        "type": "ID",
    }