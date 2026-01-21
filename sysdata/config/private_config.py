import os
import yaml
from pathlib import Path

from syscore.fileutils import resolve_path_and_filename_for_package
from syscore.constants import arg_not_supplied


DEFAULT_PRIVATE_DIR = "private"
PRIVATE_CONFIG_FILE = "private_config.yaml"
PRIVATE_CONFIG_DIR_ENV_VAR = "PYSYS_PRIVATE_CONFIG_DIR"


def get_private_config_as_dict(filename: str = arg_not_supplied) -> dict:
    private_dir = get_private_config_dir()
    if filename is arg_not_supplied:
        filename = PRIVATE_CONFIG_FILE
    try:
        private_path = resolve_path_and_filename_for_package(private_dir, filename)
        with open(private_path) as file_to_parse:
            private_dict = yaml.load(file_to_parse, Loader=yaml.FullLoader)
        return private_dict

    except Exception:
        print(
            f"Private configuration '{private_path}' is missing or "
            f"misconfigured; no problem if running in sim mode"
        )
        return {}


def get_private_config_dir():
    if os.getenv(PRIVATE_CONFIG_DIR_ENV_VAR):
        private_config_dir = Path(os.environ[PRIVATE_CONFIG_DIR_ENV_VAR])
    else:
        private_config_dir = Path(DEFAULT_PRIVATE_DIR)

    return str(private_config_dir)
