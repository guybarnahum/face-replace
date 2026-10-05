# face-replace

GPU-backed face replacement for GIF and video from 1–3 reference photos.

The tool is designed to preserve the target video's pose, expression, gaze, lighting, and motion while replacing facial identity. Occlusions such as hands, hair, glasses, and microphones should remain visually in front of the replaced face.

## v0 goal

Given:

- 1–3 reference face photos
- one GIF or video

Produce a face-replaced output while preserving:

- expression and mouth motion from the target video
- head pose and gaze
- temporal consistency
- original occlusions
- original audio for video inputs

## v0 boundary

v0 is intentionally CLI-only and runs on a single NVIDIA GPU worker.

Target runtime:

- AWS EC2 G6 / NVIDIA L4
- CUDA required for inference
- FFmpeg for media decode/encode
- NVDEC/NVENC where useful

Do not add an API, queue, object-storage workflow, Cloudflare layer, or autoscaling until the single-node CUDA path works well and has been benchmarked.

## Architecture

```text
reference photos + input media
            |
            v
      face-replace CLI
      ----------------
      FFmpeg decode
      face detection/tracking
      identity embedding
      face swap engine
      occlusion/compositing
      FFmpeg encode
            |
            v
         output media
```

## Model strategy

The engine boundary is deliberately model-agnostic. Initial evaluation should compare conventional identity-conditioned face swappers such as HyperSwap and InSwapper-class models rather than coupling the repo to one model or license.

The first benchmark suite should cover:

1. frontal talking face
2. smile / strong expression
3. profile turn
4. hand crossing the face
5. glasses, hair, or another partial occlusion

Measure identity fidelity, expression preservation, temporal stability, occlusion quality, effective FPS, and GPU cost per output minute.

## Repository layout

```text
src/face_replace/
  engine/    face-swap engine contract
  media/     FFmpeg and media handling
scripts/     benchmarking / developer tools
tests/       high-value behavior tests
docs/        architecture and decisions
```

## Status

Initial scaffold only. The next milestone is a single-video CUDA CLI baseline on an AWS G6/L4 worker before adding service infrastructure.

Target command shape:

```bash
face-replace swap \
  --reference face1.jpg \
  --reference face2.jpg \
  --target input.mp4 \
  --output output.mp4
```
