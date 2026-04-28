from unittest.mock import patch

from graphqler import __main__, config


def _make_args(path: str, **overrides):
    args = {
        "mode": "compile",
        "path": path,
        "url": None,
        "config": None,
        "schema_file": None,
    }
    args.update(overrides)
    return args


def test_compile_allows_schema_file_from_explicit_config(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCHEMA_FILE", "")
    config_path = tmp_path / "config.toml"
    schema_path = tmp_path / "schema.json"
    args = _make_args(str(tmp_path / "out"), config=str(config_path))

    def _set_config(new_config: dict):
        config.SCHEMA_FILE = new_config["SCHEMA_FILE"]

    with (
        patch("graphqler.__main__.parse_config", return_value={"SCHEMA_FILE": str(schema_path)}),
        patch("graphqler.__main__.set_config", side_effect=_set_config),
        patch("graphqler.__main__.get_or_create_directory"),
        patch("graphqler.__main__.write_config_to_toml"),
        patch("graphqler.__main__.Compiler") as compiler_cls,
        patch("graphqler.__main__.run_compile_mode"),
    ):
        __main__.main(args)

    assert compiler_cls.call_args.kwargs["schema_file"] == str(schema_path)


def test_compile_allows_schema_file_from_path_config(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "SCHEMA_FILE", "")
    output_dir = tmp_path / "out"
    output_dir.mkdir()
    schema_path = tmp_path / "schema.json"
    args = _make_args(str(output_dir))

    def _set_config(new_config: dict):
        config.SCHEMA_FILE = new_config["SCHEMA_FILE"]

    with (
        patch("graphqler.__main__.does_config_file_exist_in_path", return_value=True),
        patch("graphqler.__main__.parse_config", return_value={"SCHEMA_FILE": str(schema_path)}),
        patch("graphqler.__main__.set_config", side_effect=_set_config),
        patch("graphqler.__main__.get_or_create_directory"),
        patch("graphqler.__main__.write_config_to_toml"),
        patch("graphqler.__main__.Compiler") as compiler_cls,
        patch("graphqler.__main__.run_compile_mode"),
    ):
        __main__.main(args)

    assert compiler_cls.call_args.kwargs["schema_file"] == str(schema_path)
