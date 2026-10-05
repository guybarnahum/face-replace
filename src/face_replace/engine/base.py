from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class ReplaceRequest:
    source_faces: Sequence[Path]
    target_media: Path
    output_media: Path


class FaceReplaceEngine(ABC):
    """Minimal boundary around a face replacement implementation."""

    @abstractmethod
    def replace(self, request: ReplaceRequest) -> None:
        raise NotImplementedError
