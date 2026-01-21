from sysdata.config.configdata import Config
from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.config.private_config import get_private_config_dir
from yaml.parser import ParserError

PRIVATE_CONTROL_CONFIG_FILE = "private_control_config.yaml"
DEFAULT_CONTROL_CONFIG_FILE = "syscontrol.control_config.yaml"


def get_control_config() -> Config:
    dir = get_private_config_dir()
    private_control_path = resolve_path_and_filename_for_package(
        dir, PRIVATE_CONTROL_CONFIG_FILE
    )
    default_control_path = resolve_path_and_filename_for_package(
        DEFAULT_CONTROL_CONFIG_FILE
    )

    try:
        control_config = Config(
            private_filename=private_control_path,
            default_filename=default_control_path,
        )
        control_config.fill_with_defaults()

    except ParserError as pe:
        raise Exception("YAML syntax problem: %s" % str(pe))
    except FileNotFoundError:
        raise Exception(
            "Need to have either %s or %s or both present:"
            % (private_control_path, default_control_path)
        )
    except BaseException as be:
        raise Exception("Problem reading control config: %s" % str(be))

    return control_config
