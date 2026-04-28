from graphqler.utils.config_handler import generate_new_config


def test_generate_new_config_handles_paths_with_spaces(tmp_path):
    config_path = tmp_path / "directory with spaces" / "config.toml"

    generate_new_config(str(config_path))

    assert config_path.exists()
    assert "DEBUG = false" in config_path.read_text()
