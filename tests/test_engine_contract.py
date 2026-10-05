from pathlib import Path

from face_replace.engine.base import ReplaceRequest


def test_replace_request_supports_multiple_reference_faces() -> None:
    request = ReplaceRequest(
        source_faces=[Path("front.jpg"), Path("left.jpg"), Path("right.jpg")],
        target_media=Path("target.mp4"),
        output_media=Path("result.mp4"),
    )

    assert len(request.source_faces) == 3, "reference faces lost"
