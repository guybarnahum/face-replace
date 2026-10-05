# AGENTS.md

## Product goal

`face-replace` replaces facial identity in GIF/video using 1–3 reference photos while retaining the original performance: expression, pose, gaze, timing, lighting, and occlusions.

## v0 boundary

- CLI only.
- Target AWS EC2 G6 / NVIDIA L4.
- CUDA is required for face inference; do not silently fall back to CPU.
- Use FFmpeg for media handling and NVIDIA hardware decode/encode where it materially helps.
- Do not add APIs, queues, object-storage workflows, Cloudflare, or autoscaling until the single-node CUDA path is proven and benchmarked.

## Engineering principles

- Keep the implementation light and direct.
- Prefer a small deterministic media pipeline over framework-heavy infrastructure.
- Do not couple the product to a particular model implementation.
- Optimize the actual expensive path: decode -> detect/track -> swap -> composite -> encode.
- Avoid frame-wide generative processing when localized face processing is sufficient.
- Preserve source audio without unnecessary re-encoding.
- Chunk long videos only when it materially improves retryability, bounded memory, or parallelism.
- Add infrastructure only when a measured workload requires it.
- Treat model weights and their commercial licenses separately from repository code licenses.

## Tests

Tests should validate product behavior or important contracts, not implementation trivia. Keep failures short and meaningful. Avoid brittle image-pixel assertions when a semantic or structural assertion is sufficient.

## Near-term plan

1. Establish media probing and decode/encode path.
2. Add a CUDA runtime check.
3. Integrate one baseline face-swap engine.
4. Implement `face-replace swap` for one video and 1–3 references.
5. Add occlusion-aware compositing.
6. Build the five-clip benchmark suite.
7. Measure quality, FPS, VRAM, and cost on AWS G6/L4 before designing scaling infrastructure.
