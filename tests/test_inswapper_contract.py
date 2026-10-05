import pytest

from face_replace.providers.insightface.inswapper import InSwapperError, _single_face


def test_single_face_requires_unambiguous_input() -> None:
    with pytest.raises(InSwapperError, match="target: expected 1 face, found 2"):
        _single_face([object(), object()], "target")
