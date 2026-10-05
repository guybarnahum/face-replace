from pathlib import Path

import numpy as np

from face_replace.engine.base import FaceReplaceEngine, FaceReplaceSession


class Session(FaceReplaceSession):
    def replace(self, frame):
        return frame


class Engine(FaceReplaceEngine):
    def __init__(self) -> None:
        self.references = []

    def fetch_assets(self):
        return []

    def prepare(self, references):
        self.references = list(references)
        return Session()


def test_engine_contract_keeps_reference_set() -> None:
    engine = Engine()
    session = engine.prepare(
        [Path("front.jpg"), Path("left.jpg"), Path("right.jpg")]
    )

    frame = np.zeros((2, 2, 3), dtype=np.uint8)

    assert len(engine.references) == 3, "reference set lost"
    assert session.replace(frame) is frame, "session changed frame contract"
