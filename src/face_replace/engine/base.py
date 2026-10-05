from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence

import numpy as np
from numpy.typing import NDArray


Frame = NDArray[np.uint8]


class FaceReplaceError(RuntimeError):
    pass


class FaceReplaceSession(ABC):
    """Prepared identity + loaded model, reusable across target frames."""

    @abstractmethod
    def replace(self, frame: Frame) -> Frame:
        raise NotImplementedError


class FaceReplaceEngine(ABC):
    """Provider/model-neutral face replacement contract."""

    @abstractmethod
    def fetch_assets(self) -> Sequence[Path]:
        """Ensure every artifact required by the configured model is cached."""
        raise NotImplementedError

    @abstractmethod
    def prepare(self, references: Sequence[Path]) -> FaceReplaceSession:
        """Load the model and prepare source identity once for repeated frames."""
        raise NotImplementedError
