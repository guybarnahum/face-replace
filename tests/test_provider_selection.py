import pytest

from face_replace.config import RuntimeConfig
from face_replace.engine.base import FaceReplaceError
from face_replace.providers.insightface import create_engine


def test_unknown_insightface_model_fails_concisely() -> None:
    config = RuntimeConfig(provider="insightface", model="unknown")

    with pytest.raises(FaceReplaceError, match="does not support model 'unknown'"):
        create_engine(config)
