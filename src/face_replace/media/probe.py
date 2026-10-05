from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class MediaInfo:
    width: int
    height: int
    duration_seconds: float
    fps: float


def probe(path: Path) -> MediaInfo:
    command = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate:format=duration",
        "-of", "json",
        str(path),
    ]
    result = subprocess.run(command, check=True, capture_output=True, text=True)
    payload = json.loads(result.stdout)
    stream = payload["streams"][0]
    numerator, denominator = map(int, stream["r_frame_rate"].split("/"))
    return MediaInfo(
        width=int(stream["width"]),
        height=int(stream["height"]),
        duration_seconds=float(payload["format"]["duration"]),
        fps=numerator / denominator,
    )
