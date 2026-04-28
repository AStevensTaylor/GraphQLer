from pathlib import Path
import shutil
import tomllib

from graphqler import config
from graphqler.utils.file_utils import get_graphqler_root


def write_config_to_toml(path: str) -> None:
    """Write current live-config values to a TOML file.

    Reads ``examples/config.toml`` to discover the canonical set of
    user-configurable keys — no static list required.  For each key in the
    template, the current value is read from the live ``config`` module so
    any in-process changes are captured.  Keys absent from the live module
    fall back to the template's default value.

    Sensitive fields (``LLM_API_KEY``, ``IDOR_SECONDARY_AUTH``, ``AUTHORIZATION``)
    are always written as empty strings so that secrets provided via CLI flags
    or environment variables are not accidentally persisted to disk.
    """
    # Fields that must never be written to disk
    _REDACTED_FIELDS = {"LLM_API_KEY", "IDOR_SECONDARY_AUTH", "AUTHORIZATION"}

    template_path = get_graphqler_root() / "examples" / "config.toml"
    with open(template_path, "rb") as fh:
        template: dict = tomllib.load(fh)

    lines = ["# GraphQLer configuration\n"]
    for key, template_value in template.items():
        if key in {"CUSTOM_HEADERS", "CUSTOM_SCALARS"}:
            continue  # written as a TOML section below
        if key in _REDACTED_FIELDS:
            lines.append(f'{key} = ""\n')
            continue
        value = getattr(config, key, template_value)
        if isinstance(value, bool):
            lines.append(f"{key} = {'true' if value else 'false'}\n")
        elif isinstance(value, (int, float)):
            lines.append(f"{key} = {value}\n")
        elif isinstance(value, list):
            # Emit a proper TOML inline array; strings are quoted and escaped
            def _toml_item(item) -> str:
                if isinstance(item, str):
                    return '"' + item.replace("\\", "\\\\").replace('"', '\\"') + '"'
                return str(item)
            items = ", ".join(_toml_item(item) for item in value)
            lines.append(f"{key} = [{items}]\n")
        elif value is None:
            lines.append(f'{key} = ""\n')
        else:
            escaped = str(value).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{key} = "{escaped}"\n')

    for section_name in ("CUSTOM_HEADERS", "CUSTOM_SCALARS"):
        lines.append(f"\n[{section_name}]\n")
        section_values: dict = getattr(config, section_name, None) or template.get(section_name, {})
        for k, v in section_values.items():
            ev = str(v).replace("\\", "\\\\").replace('"', '\\"')
            lines.append(f'{k} = "{ev}"\n')

    with open(path, "w") as fh:
        fh.writelines(lines)


def parse_config(config_obj: str | dict) -> dict:
    """
    Parse the config, and return the dictionary.
    If it's a dictionary, just parses the config object directly
    Otherwise parses it out of a TOML file
    """
    config = {}
    if isinstance(config_obj, dict):
        config = config_obj
    elif isinstance(config_obj, str):
        with open(config_obj, "rb") as f:
            config = tomllib.load(f)

    if len(config.keys()) == 0:
        print(f"(!) No items in config {config_obj}")
        exit(1)

    return config


def set_config(new_config: dict):
    """Sets config to the new file using reflection on the constants module

    Args:
        new_config (dict): The configuration dictionary
    """
    for k, v in new_config.items():
        if hasattr(config, k):
            setattr(config, k, v)
        else:
            print(f"(!) Unknown configuration {k}, skipping it")


def generate_new_config(config_file_to_write: str) -> None:
    """Generates the new config file by copying from static/config.toml

    Args:
        config_file_to_write (str): The config file to write
    """
    project_root = get_graphqler_root()
    source = project_root / "examples" / "config.toml"
    destination = Path(config_file_to_write)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(source, destination)


def does_config_file_exist_in_path(path: str) -> bool:
    """Checks if the config file exists in the path

    Args:
        path (str): The path to check

    Returns:
        bool: Whether the config file exists
    """
    return Path(path, config.CONFIG_FILE_NAME).exists()
