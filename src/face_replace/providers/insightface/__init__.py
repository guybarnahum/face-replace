from __future__ import annotations

from face_replace.config import RuntimeConfig
from face_replace.engine.base import FaceReplaceEngine, FaceReplaceError


def create_engine(config: RuntimeConfig) -> FaceReplaceEngine:
    if config.model == "inswapper_128":
        from .inswapper import InSwapperEngine

        return InSwapperEngine(config)

    raise FaceReplaceError(
        f"insightface does not support model {config.model!r}"
    )
