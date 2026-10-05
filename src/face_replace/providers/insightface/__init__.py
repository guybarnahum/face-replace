from __future__ import annotations

from face_replace.config import RuntimeConfig
from face_replace.engine.base import FaceReplaceEngine


def create_engine(config: RuntimeConfig) -> FaceReplaceEngine:
    if config.model == "inswapper_128":
        from .inswapper import InSwapperEngine

        return InSwapperEngine(config)

    raise ValueError(
        f"insightface does not support model {config.model!r}"
    )
