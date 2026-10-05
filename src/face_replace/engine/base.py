from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Sequence

import numpy as np
from numpy.typing import NDArray


Frame = NDArray[np.uint8]


class FaceReplaceSession(ABC):
    """Prepared identity + loaded model, reusable across target frames."""

    @abstractmethod
    def replace(self, frame: Frame) -> Frame:
        raise NotImplementedError


class FaceReplaceEngine(ABC):
    """Provider/model-neutral face replacement contract."""

    @abstractmethod
    def fetch_models(self) -> Sequence[Path]:
        """Ensure this engine's model artifacts are present locally."""
        raise NotImplementedError

    @abstractmethod
    def prepare(self, references: Sequence[Path]) -> FaceReplaceSession:
        """Load models and prepare source identity once for repeated frames."""
        raise NotImplementedError
