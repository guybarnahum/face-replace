# AGENTS.md

## Product goal

`face-replace` replaces facial identity in GIF/video using 1–3 reference photos while retaining the original performance: expression, pose, gaze, timing, lighting, and occlusions.

## Engineering principles

- Keep the implementation light and direct.
- Prefer a small deterministic media pipeline over a framework-heavy service.
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
2. Define the face-swap engine contract.
3. Integrate one baseline engine.
4. Add occlusion-aware compositing.
5. Build the five-clip benchmark suite.
6. Measure an AWS G6/L4 worker before designing scaling infrastructure.
