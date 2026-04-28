"""Unit tests for ObjectDependencyResolver custom scalar handling."""

from graphqler import config
from graphqler.compiler.resolvers.object_dependency_resolver import ObjectDependencyResolver


def test_configured_custom_scalar_is_not_treated_as_object_dependency():
    original_custom_scalars = dict(config.CUSTOM_SCALARS)
    config.CUSTOM_SCALARS = {"UUID": "uuid"}

    try:
        gql_object = {
            "fields": [
                {
                    "name": "workspaceId",
                    "kind": "SCALAR",
                    "type": "UUID",
                    "inputs": {},
                    "ofType": None,
                }
            ]
        }

        result = ObjectDependencyResolver().parse_gql_object(gql_object)

        assert result["softDependsOn"] == []
        assert result["hardDependsOn"] == []
    finally:
        config.CUSTOM_SCALARS = original_custom_scalars