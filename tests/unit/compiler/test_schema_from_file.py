"""Unit tests for Compiler.load_schema_from_file."""

import json
import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

# Minimal valid introspection envelope (same structure as the live fixture)
_MINIMAL_SCHEMA = {
    "data": {
        "__schema": {
            "queryType": {"name": "Query"},
            "mutationType": None,
            "subscriptionType": None,
            "types": [
                {
                    "kind": "OBJECT",
                    "name": "Query",
                    "description": None,
                    "fields": [],
                    "inputFields": None,
                    "interfaces": [],
                    "enumValues": None,
                    "possibleTypes": None,
                }
            ],
            "directives": [],
        }
    }
}

# Raw __schema format (no "data" wrapper) — some tools emit this
_RAW_SCHEMA = {
    "__schema": _MINIMAL_SCHEMA["data"]["__schema"]
}


def _write_json(tmp_path: Path, data: dict, filename: str = "schema.json") -> str:
    p = tmp_path / filename
    p.write_text(json.dumps(data))
    return str(p)


def _make_compiler(tmp_path: Path, schema_file: str = ""):
    """Return a Compiler instance with all heavy I/O mocked out."""
    with (
        patch("graphqler.compiler.compiler.plugins_handler"),
        patch("graphqler.compiler.compiler.Logger"),
        patch("graphqler.compiler.compiler.initialize_file"),
        patch("graphqler.compiler.compiler.intialize_file_if_not_exists"),
    ):
        from graphqler.compiler.compiler import Compiler
        c = Compiler(str(tmp_path), url="http://example.com", schema_file=schema_file)
        # Point to a path inside tmp_path so real writes land in the temp dir
        c.introspection_result_save_path = tmp_path / "introspection_result.json"
        return c


class TestLoadSchemaFromFile:
    def test_loads_envelope_format(self, tmp_path):
        """Envelope format {"data": {"__schema": ...}} is returned unchanged."""
        compiler = _make_compiler(tmp_path)
        path = _write_json(tmp_path, _MINIMAL_SCHEMA)
        result = compiler.load_schema_from_file(path)
        assert result["data"]["__schema"]["queryType"]["name"] == "Query"

    def test_loads_raw_schema_format(self, tmp_path):
        """Raw format {"__schema": ...} is wrapped in the expected envelope."""
        compiler = _make_compiler(tmp_path)
        path = _write_json(tmp_path, _RAW_SCHEMA)
        result = compiler.load_schema_from_file(path)
        assert "data" in result
        assert "__schema" in result["data"]
        assert result["data"]["__schema"]["queryType"]["name"] == "Query"

    def test_saves_result_to_disk(self, tmp_path):
        """The loaded result is persisted to introspection_result_save_path."""
        compiler = _make_compiler(tmp_path)
        path = _write_json(tmp_path, _MINIMAL_SCHEMA)
        compiler.load_schema_from_file(path)
        saved_path = compiler.introspection_result_save_path
        assert saved_path.exists()
        saved = json.loads(saved_path.read_text())
        assert saved["data"]["__schema"]["queryType"]["name"] == "Query"

    def test_raises_on_missing_file(self, tmp_path):
        compiler = _make_compiler(tmp_path)
        with pytest.raises(SystemExit, match="not found"):
            compiler.load_schema_from_file("/nonexistent/path/schema.json")

    def test_raises_on_invalid_json(self, tmp_path):
        compiler = _make_compiler(tmp_path)
        bad = tmp_path / "bad.json"
        bad.write_text("this is not json {{{")
        with pytest.raises(SystemExit, match="not valid JSON"):
            compiler.load_schema_from_file(str(bad))

    def test_raises_on_unrecognised_structure(self, tmp_path):
        compiler = _make_compiler(tmp_path)
        path = _write_json(tmp_path, {"something": "else"})
        with pytest.raises(SystemExit, match="recognisable"):
            compiler.load_schema_from_file(path)


class TestCompilerRunUsesSchemaFile:
    def test_run_skips_introspection_when_schema_file_set(self, tmp_path):
        """When schema_file is provided, run() calls load_schema_from_file and skips
        get_introspection_query_results."""
        schema_path = _write_json(tmp_path, _MINIMAL_SCHEMA)
        compiler = _make_compiler(tmp_path, schema_file=schema_path)

        compiler.run_parsers_and_save = MagicMock()
        compiler.run_resolvers_and_save = MagicMock()
        compiler.get_introspection_query_results = MagicMock()

        compiler.run()

        compiler.get_introspection_query_results.assert_not_called()
        compiler.run_parsers_and_save.assert_called_once()
        compiler.run_resolvers_and_save.assert_called_once()

    def test_run_falls_back_to_introspection_when_no_schema_file(self, tmp_path):
        """When schema_file is empty, run() calls get_introspection_query_results."""
        compiler = _make_compiler(tmp_path)

        compiler.get_introspection_query_results = MagicMock(return_value=_MINIMAL_SCHEMA)
        compiler.run_parsers_and_save = MagicMock()
        compiler.run_resolvers_and_save = MagicMock()

        compiler.run()

        compiler.get_introspection_query_results.assert_called_once()
        compiler.run_parsers_and_save.assert_called_once()
