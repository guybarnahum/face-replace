from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, Field
import yaml


class ConfigError(RuntimeError):
    pass


class RuntimeConfig(BaseModel):
    provider: str
    model: str
    device: Literal["cuda"] = "cuda"
    device_id: int = Field(default=0, ge=0)
    models_dir: Path = Path("models")
    options: dict[str, Any] = Field(default_factory=dict)


class AppConfig(BaseModel):
    runtime: RuntimeConfig


def load_config(path: Path | str = "config.yaml") -> AppConfig:
    config_path = Path(path).expanduser().resolve()
    if not config_path.is_file():
        raise ConfigError(f"config not found: {config_path}")

    try:
        raw = yaml.safe_load(config_path.read_text()) or {}
        config = AppConfig.model_validate(raw)
    except Exception as exc:
        raise ConfigError(f"invalid config: {exc}") from exc

    models_dir = config.runtime.models_dir
    if not models_dir.is_absolute():
        models_dir = (config_path.parent / models_dir).resolve()

    return config.model_copy(
        update={
            "runtime": config.runtime.model_copy(
                update={"models_dir": models_dir}
            )
        }
    )
