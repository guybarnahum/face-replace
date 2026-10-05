from __future__ import annotations

from pathlib import Path
from typing import Sequence

from face_replace.engine.base import FaceReplaceEngine


class ImageReplaceError(RuntimeError):
    pass


def replace_image(
    engine: FaceReplaceEngine,
    references: Sequence[Path],
    target: Path,
    output: Path,
) -> Path:
    import cv2

    image = cv2.imread(str(target))
    if image is None:
        raise ImageReplaceError(f"unable to read target image: {target}")

    session = engine.prepare(references)
    result = session.replace(image)

    output.parent.mkdir(parents=True, exist_ok=True)
    if not cv2.imwrite(str(output), result):
        raise ImageReplaceError(f"unable to write output image: {output}")

    return output
