from __future__ import annotations

from dataclasses import dataclass
import shutil
import subprocess


@dataclass(frozen=True)
class Check:
    label: str
    ok: bool
    detail: str


def _run(*command: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
    )


def _nvidia() -> Check:
    if not shutil.which("nvidia-smi"):
        return Check("NVIDIA GPU", False, "nvidia-smi not found")

    result = _run(
        "nvidia-smi",
        "--query-gpu=name,driver_version,memory.total",
        "--format=csv,noheader,nounits",
    )
    if result.returncode != 0:
        return Check("NVIDIA GPU", False, result.stderr.strip() or "nvidia-smi failed")

    parts = [part.strip() for part in result.stdout.strip().split(",")]
    if len(parts) != 3:
        return Check("NVIDIA GPU", False, "unexpected nvidia-smi output")

    name, driver, memory_mib = parts
    return Check("NVIDIA GPU", True, f"{name} · {memory_mib} MiB · driver {driver}")


def _onnx_cuda() -> Check:
    try:
        import onnxruntime as ort
    except Exception as exc:
        return Check("ONNX Runtime", False, f"import failed: {exc}")

    try:
        ort.preload_dlls(directory="")
    except Exception as exc:
        return Check("ONNX Runtime", False, f"CUDA libraries failed to load: {exc}")

    providers = ort.get_available_providers()
    if "CUDAExecutionProvider" not in providers:
        return Check(
            "ONNX Runtime",
            False,
            f"CUDAExecutionProvider unavailable · providers: {', '.join(providers)}",
        )

    return Check(
        "ONNX Runtime",
        True,
        f"{ort.__version__} · CUDAExecutionProvider",
    )


def _ffmpeg() -> tuple[Check, Check]:
    if not shutil.which("ffmpeg"):
        missing = Check("FFmpeg", False, "ffmpeg not found")
        return missing, Check("NVIDIA codecs", False, "ffmpeg not found")

    version = _run("ffmpeg", "-hide_banner", "-version")
    if version.returncode != 0:
        detail = version.stderr.strip() or "ffmpeg failed"
        return Check("FFmpeg", False, detail), Check("NVIDIA codecs", False, detail)

    first_line = version.stdout.splitlines()[0] if version.stdout else "ffmpeg"
    ffmpeg_check = Check("FFmpeg", True, first_line)

    encoders = _run("ffmpeg", "-hide_banner", "-encoders")
    hwaccels = _run("ffmpeg", "-hide_banner", "-hwaccels")
    encoder_text = encoders.stdout
    hwaccel_text = hwaccels.stdout

    available = [
        codec
        for codec in ("h264_nvenc", "hevc_nvenc", "av1_nvenc")
        if codec in encoder_text
    ]
    cuda_hwaccel = "cuda" in {line.strip() for line in hwaccel_text.splitlines()}

    details = []
    if available:
        details.append(", ".join(available))
    if cuda_hwaccel:
        details.append("CUDA hwaccel")

    ok = bool(available) and cuda_hwaccel
    return ffmpeg_check, Check(
        "NVIDIA codecs",
        ok,
        " · ".join(details) if details else "NVENC/CUDA support not found",
    )


def checks() -> list[Check]:
    ffmpeg, codecs = _ffmpeg()
    return [_nvidia(), _onnx_cuda(), ffmpeg, codecs]


def print_doctor() -> bool:
    results = checks()

    print("face-replace doctor")
    print("───────────────────")
    for result in results:
        mark = "✓" if result.ok else "✗"
        print(f"  {mark} {result.label:<15} {result.detail}")

    ready = all(result.ok for result in results)
    print()
    print(f"Ready: {'yes' if ready else 'no'}")
    return ready
