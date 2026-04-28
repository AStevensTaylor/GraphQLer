"""Unit tests for MutationListParser."""

from graphqler.compiler.parsers.mutation_list_parser import MutationListParser


def test_parses_mutation_when_description_is_missing():
    data = {
        "data": {
            "__schema": {
                "types": [
                    {
                        "kind": "OBJECT",
                        "name": "Mutation",
                        "fields": [
                            {
                                "name": "createItem",
                                "args": [],
                                "isDeprecated": False,
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

    result = MutationListParser().parse(data)

    assert result["createItem"]["description"] is None
    assert result["createItem"]["output"] == {
        "kind": "OBJECT",
        "name": "Item",
        "ofType": None,
        "type": "Item",
    }