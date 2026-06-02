import json
from pathlib import Path

from omegaconf import OmegaConf

from syscore.fileutils import resolve_path_and_filename_for_package
from sysdata.config.configdata import Config


def _trading_rule_to_func_path(rule) -> str:
    func = rule.function
    return f"{func.__module__}.{func.__qualname__}"


def _trading_rule_to_interpolation(rule) -> str:
    """Serialize a TradingRule to a ${pst_trading_rule:<hex>} interpolation string.

    Hex encoding (0-9a-f only) avoids any OmegaConf grammar issues — commas in
    JSON would be mis-parsed as resolver argument separators, and base64 padding
    '=' is not valid in OmegaConf interpolation syntax.
    """
    payload = {
        "function": _trading_rule_to_func_path(rule),
        "data": rule.data,
        "other_args": rule.other_args,
        "data_args": rule.data_args,
    }
    encoded = json.dumps(payload).encode().hex()
    return f"${{pst_trading_rule:{encoded}}}"


def _trading_rule_to_yaml_dict(rule) -> dict:
    """Convert a TradingRule to its canonical dict form for YAML serialisation."""
    return {
        "function": _trading_rule_to_func_path(rule),
        "data": rule.data,
        "other_args": rule.other_args,
    }


def _resolve_pst_trading_rule(encoded: str):
    """OmegaConf resolver: base64-encoded JSON → TradingRule."""
    from systems.trading_rules import TradingRule
    from syscore.objects import resolve_function

    payload = json.loads(bytes.fromhex(encoded).decode())

    # Bypass TradingRule.__init__ to avoid recomputing data_args from other_args;
    # the serialised payload already carries the resolved data_args.
    rule = object.__new__(TradingRule)
    rule._function = resolve_function(payload["function"])
    rule._data = payload["data"]
    rule._other_args = payload["other_args"]
    rule._data_args = payload["data_args"]
    return rule


# Register once per process.  replace=True is safe for test reruns.
OmegaConf.register_new_resolver(
    "pst_trading_rule", _resolve_pst_trading_rule, replace=True
)


def _convert_for_omegaconf(obj):
    """Recursively replace TradingRule objects with resolver interpolation strings."""
    from systems.trading_rules import TradingRule

    if isinstance(obj, TradingRule):
        return _trading_rule_to_interpolation(obj)
    if isinstance(obj, dict):
        return {k: _convert_for_omegaconf(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_for_omegaconf(v) for v in obj]
    return obj


def _convert_for_save(obj):
    """Recursively replace TradingRule objects with their YAML-canonical dict form."""
    from systems.trading_rules import TradingRule

    if isinstance(obj, TradingRule):
        return _trading_rule_to_yaml_dict(obj)
    if isinstance(obj, dict):
        return {k: _convert_for_save(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_convert_for_save(v) for v in obj]
    return obj


class OmegaConfConfig(Config):
    def _create_config_from_item(self, config_item):
        if isinstance(config_item, dict):
            self._create_config_from_dict(config_item)

        elif isinstance(config_item, (str, Path)):
            filename = resolve_path_and_filename_for_package(config_item)
            cfg = OmegaConf.load(filename)
            self._create_config_from_dict(OmegaConf.to_container(cfg, resolve=True))

        elif isinstance(config_item, Config):
            self._create_config_from_dict(config_item.as_dict())

        else:
            self.log.critical(
                "Can only create a config with a nested dict or the "
                "string of a 'yamable' filename, or a list "
                "comprising these things"
            )

    def fill_with_defaults(self):
        # Convert any TradingRule objects to resolver interpolation strings so
        # OmegaConf.create() can wrap the dict (OmegaConf only accepts primitives).
        # to_container(resolve=True) fires the resolver and restores TradingRule objects.
        safe_dict = _convert_for_omegaconf(self.as_dict())

        # OmegaConf.merge: later configs win — priority is self > private > defaults
        merged = OmegaConf.merge(
            OmegaConf.create(self.default_config_dict),
            OmegaConf.create(self.private_config_dict),
            OmegaConf.create(safe_dict),
        )
        self._create_config_from_dict(OmegaConf.to_container(merged, resolve=True))

    def save(self, filename):
        saveable = _convert_for_save(self.as_dict())
        OmegaConf.save(OmegaConf.create(saveable), filename)
