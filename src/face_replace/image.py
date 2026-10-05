from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Sequence

from face_replace.engine.base import FaceReplaceEngine, FaceReplaceError


@dataclass(frozen=True)
class ImageReplaceResult:
    output: Path
    prepare_seconds: float
    replace_seconds: float


class ImageReplaceError(FaceReplaceError):
    pass


def replace_image(
    engine: FaceReplaceEngine,
    references: Sequence[Path],
    target: Path,
    output: Path,
) -> ImageReplaceResult:
    import cv2

    image = cv2.imread(str(target))
    if image is None:
        raise ImageReplaceError(f"unable to read target image: {target}")

    started = perf_counter()
    session = engine.prepare(references)
    prepared = perf_counter()

    result = session.replace(image)
    replaced = perf_counter()

    output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output), result):
        raise ImageReplaceError(f"unable to write output image: {output}")

    return ImageReplaceResult(
        output=output,
        prepare_seconds=prepared - started,
        replace_seconds=replaced - prepared,
    )
