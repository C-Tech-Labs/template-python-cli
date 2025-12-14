"""Configuration helpers for the CLI template.

The module provides a typed configuration object alongside helper functions to
load settings from files, environment variables, and command-line arguments.
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable

DEFAULT_ENV_PREFIX = "TEMPLATECLI_"


@dataclass(slots=True)
class AppConfig:
    """Runtime configuration for the CLI."""

    name: str = "world"
    greeting: str = "Hello"
    punctuation: str = "!"
    repeat: int = 1
    loud: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if self.repeat < 1:
            raise ValueError("repeat must be at least 1")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "greeting": self.greeting,
            "punctuation": self.punctuation,
            "repeat": self.repeat,
            "loud": self.loud,
            "metadata": self.metadata,
        }


def _coerce_bool(value: str) -> bool:
    truthy = {"1", "true", "t", "yes", "y", "on"}
    falsy = {"0", "false", "f", "no", "n", "off"}
    lowered = value.strip().lower()
    if lowered in truthy:
        return True
    if lowered in falsy:
        return False
    raise ValueError(f"Cannot interpret boolean value from '{value}'")


def load_config_file(path: Path | None) -> Dict[str, Any]:
    """Load configuration from a YAML or JSON file.

    Args:
        path: Optional path to a YAML or JSON file.

    Returns:
        A dictionary with configuration keys.
    """

    if path is None:
        return {}

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    suffix = path.suffix.lower()
    content = path.read_text(encoding="utf-8")
    if suffix in {".yaml", ".yml"}:
        data = _load_yaml_module().safe_load(content)
    elif suffix == ".json":
        data = json.loads(content)
    else:
        raise ValueError(f"Unsupported config extension '{suffix}'. Use .yaml or .json.")

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError("Configuration file must define a mapping at the top level")
    return data


def load_environment(prefix: str = DEFAULT_ENV_PREFIX) -> Dict[str, Any]:
    """Load configuration overrides from environment variables."""

    keys = {
        "name": str,
        "greeting": str,
        "punctuation": str,
        "repeat": int,
        "loud": bool,
    }

    env_config: Dict[str, Any] = {}
    for key, caster in keys.items():
        env_key = f"{prefix}{key.upper()}"
        if env_key not in os.environ:
            continue
        raw_value = os.environ[env_key]
        if caster is bool:
            env_config[key] = _coerce_bool(raw_value)
        elif caster is int:
            env_config[key] = int(raw_value)
        else:
            env_config[key] = raw_value
    return env_config


def merge_configurations(*configs: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
    """Merge multiple configuration dictionaries preserving later overrides."""

    merged: Dict[str, Any] = {}
    for config in configs:
        merged.update({k: v for k, v in config.items() if v is not None})
    return merged


def build_config(file_config: Dict[str, Any], env_config: Dict[str, Any], cli_config: Dict[str, Any]) -> AppConfig:
    """Create an AppConfig from layered sources."""

    merged = merge_configurations(asdict(AppConfig()), file_config, env_config, cli_config)
    config = AppConfig(
        name=str(merged.get("name", "world")),
        greeting=str(merged.get("greeting", "Hello")),
        punctuation=str(merged.get("punctuation", "!")),
        repeat=int(merged.get("repeat", 1)),
        loud=bool(merged.get("loud", False)),
        metadata=merged.get("metadata", {}) or {},
    )
    config.validate()
    return config


def _load_yaml_module():
    try:
        import yaml  # type: ignore
    except ModuleNotFoundError as exc:  # pragma: no cover - exercised via integration
        raise ImportError(
            "PyYAML is required for YAML configs. Install the optional 'yaml' extra: "
            "pip install template-python-cli[yaml]"
        ) from exc
    return yaml
