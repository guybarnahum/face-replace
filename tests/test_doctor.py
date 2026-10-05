from face_replace.doctor import Check


def test_cuda_provider_failure_is_not_silently_accepted() -> None:
    result = Check(
        label="ONNX Runtime",
        ok=False,
        detail="CUDAExecutionProvider unavailable",
    )

    assert not result.ok, "CPU fallback accepted"
