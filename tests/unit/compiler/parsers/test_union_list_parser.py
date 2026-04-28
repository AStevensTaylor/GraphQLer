"""Unit tests for UnionListParser."""

from graphqler.compiler.parsers.union_list_parser import UnionListParser


def test_parses_possible_types_without_explicit_oftype_key():
    data = {
        "data": {
            "__schema": {
                "types": [
                    {
                        "kind": "UNION",
                        "name": "SearchResult",
                        "possibleTypes": [
                            {"kind": "OBJECT", "name": "Project"},
                            {"kind": "OBJECT", "name": "Item"},
                        ],
                    }
                ]
            }
        }
    }

    result = UnionListParser().parse(data)

    assert result == {
        "SearchResult": {
            "possibleTypes": [
                {"kind": "OBJECT", "name": "Project", "ofType": None, "type": "Project"},
                {"kind": "OBJECT", "name": "Item", "ofType": None, "type": "Item"},
            ]
        }
    }