from __future__ import annotations

from importlib import import_module

from face_replace.config import RuntimeConfig
from face_replace.engine.base import FaceReplaceEngine


class RuntimeConfigError(RuntimeError):
    pass


_PROVIDERS = {
    "insightface": "face_replace.providers.insightface",
}


def create_engine(config: RuntimeConfig) -> FaceReplaceEngine:
    if config.device != "cuda":
        raise RuntimeConfigError("face-replace v0 requires device: cuda")

    module_name = _PROVIDERS.get(config.provider)
    if module_name is None:
        supported = ", ".join(sorted(_PROVIDERS))
        raise RuntimeConfigError(
            f"unknown provider {config.provider!r}; supported: {supported}"
        )

    module = import_module(module_name)
    return module.create_engine(config)
