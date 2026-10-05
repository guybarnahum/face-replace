# face-replace slice plan

## North star

Given 1–3 photos of a person and a GIF or video, produce a convincing identity replacement while preserving the original performance: expression, gaze, pose, timing, lighting, occlusions, motion, and audio.

The implementation should stay lightweight and efficient: localized face inference, CUDA on a single EC2 GPU, minimal decoding/re-encoding, and no service infrastructure until quality and performance justify it.

## Status

### R1 — CUDA runtime + media foundation — complete

Validated on AWS EC2 with an NVIDIA L4:

- NVIDIA L4 visible: 23034 MiB VRAM
- NVIDIA driver: 580.159.03
- ONNX Runtime: 1.30.0
- CUDAExecutionProvider available
- FFmpeg: 4.4.2
- CUDA hardware acceleration available
- NVENC: h264_nvenc and hevc_nvenc available
- `face-replace doctor`: Ready: yes
- tests: 2 passed

### R2 — one-frame identity replacement — next

Goal: prove identity replacement quality before adding video complexity.

Scope:

1. Choose one baseline swap model with usable licensing for evaluation.
2. Add model download/cache tooling without committing weights.
3. Detect one reference face and one target face.
4. Run the swap with CUDA only.
5. Composite the replaced face back into the target image.
6. Add a small CLI surface for image-to-image validation.
7. Record inference time and peak GPU memory.

Acceptance:

- recognizable reference identity
- target pose and expression preserved
- frontal and moderate-angle targets work
- CUDA is actually used
- no silent CPU fallback
- concise failure for missing/invalid faces
- no unnecessary video, tracking, queueing, or API work

### R3 — short-video end to end

Decode -> detect -> swap -> composite -> encode, preserving original audio.

### R4 — temporal stability + tracking

Track the intended face and avoid frame-to-frame identity or crop jitter.

### R5 — 1–3 reference identity quality

Use multiple reference images to improve identity robustness across pose.

### R6 — occlusion-aware compositing

Preserve hands, hair, glasses, microphones, and other foreground occlusions.

### R7 — benchmark + model bake-off

Compare identity fidelity, expression retention, temporal stability, occlusion quality, FPS, VRAM, and GPU cost per output minute.

### R8 — GIF + long-video robustness

Stream ordinary videos; chunk only when retryability or bounded resource use makes it worthwhile.

### R9 — EC2 packaging

Fresh GPU machine -> clone -> setup -> doctor -> swap with very few commands.

### R10 — north-star quality polish

Focus on visible failures: extreme yaw, motion blur, tiny faces, partial visibility, strong expressions, scene cuts, and lighting mismatch.
