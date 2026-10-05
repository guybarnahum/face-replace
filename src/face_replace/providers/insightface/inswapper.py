from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Sequence

import numpy as np

from face_replace.config import RuntimeConfig
from face_replace.engine.base import FaceReplaceEngine, FaceReplaceSession, Frame


_MODEL_URL = (
    "https://huggingface.co/tsi-org/face-swapper/"
    "resolve/main/inswapper_128.onnx?download=true"
)
_MODEL_SHA256 = "e4a3f08c753cb72d04e10aa0f7dbe3deebbf39567d4ead6dce08e98aa49e16af"


class InSwapperError(RuntimeError):
    pass


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _single_face(faces: Sequence[object], label: str) -> object:
    if len(faces) != 1:
        raise InSwapperError(f"{label}: expected 1 face, found {len(faces)}")
    return faces[0]


def _strict_cuda(device_id: int):
    import onnxruntime as ort

    options = ort.SessionOptions()
    options.add_session_config_entry("session.disable_cpu_ep_fallback", "1")
    providers = [
        ("CUDAExecutionProvider", {"device_id": device_id}),
    ]
    return options, providers


class InSwapperSession(FaceReplaceSession):
    def __init__(self, analysis, swapper, source_face) -> None:
        self.analysis = analysis
        self.swapper = swapper
        self.source_face = source_face

    def replace(self, frame: Frame) -> Frame:
        target_face = _single_face(self.analysis.get(frame), "target")
        return self.swapper.get(
            frame,
            target_face,
            self.source_face,
            paste_back=True,
        )


class InSwapperEngine(FaceReplaceEngine):
    """InsightFace/InSwapper adapter. Evaluation weights require separate licensing."""

    def __init__(self, config: RuntimeConfig) -> None:
        self.config = config
        self.root = config.models_dir / "insightface"
        self.model_path = self.root / "inswapper_128.onnx"

    def fetch_models(self) -> Sequence[Path]:
        import requests
        from insightface.utils import ensure_available

        self.root.mkdir(parents=True, exist_ok=True)

        if not self.model_path.is_file() or _sha256(self.model_path) != _MODEL_SHA256:
            partial = self.model_path.with_suffix(".onnx.part")
            with requests.get(_MODEL_URL, stream=True, timeout=60) as response:
                response.raise_for_status()
                with partial.open("wb") as output:
                    for chunk in response.iter_content(chunk_size=1024 * 1024):
                        if chunk:
                            output.write(chunk)

            actual = _sha256(partial)
            if actual != _MODEL_SHA256:
                partial.unlink(missing_ok=True)
                raise InSwapperError(
                    f"model checksum mismatch: expected {_MODEL_SHA256}, got {actual}"
                )
            partial.replace(self.model_path)

        buffalo = Path(
            ensure_available(
                "models",
                "buffalo_l",
                root=str(self.root),
            )
        )
        return [self.model_path, buffalo]

    def prepare(self, references: Sequence[Path]) -> FaceReplaceSession:
        if len(references) != 1:
            raise InSwapperError(
                f"inswapper_128 R2 expects 1 reference, found {len(references)}"
            )
        if not self.model_path.is_file():
            raise InSwapperError(
                "model missing; run: face-replace models fetch"
            )

        import cv2
        import insightface
        from insightface.app import FaceAnalysis

        session_options, providers = _strict_cuda(self.config.device_id)

        analysis = FaceAnalysis(
            name="buffalo_l",
            root=str(self.root),
            allowed_modules=["detection", "recognition"],
            providers=providers,
            sess_options=session_options,
        )
        analysis.prepare(
            ctx_id=self.config.device_id,
            det_size=(640, 640),
        )

        swapper = insightface.model_zoo.get_model(
            str(self.model_path),
            providers=providers,
            sess_options=session_options,
        )
        if swapper is None:
            raise InSwapperError("unable to load inswapper_128")

        reference = Path(references[0])
        image = cv2.imread(str(reference))
        if image is None:
            raise InSwapperError(f"unable to read reference image: {reference}")

        source_face = _single_face(analysis.get(image), "reference")
        return InSwapperSession(analysis, swapper, source_face)
