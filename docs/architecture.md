# Architecture

## Principle

Keep identity replacement separate from media transport and infrastructure.

The expensive operation is per-frame face inference. Everything around it should minimize copies, redundant decoding, and re-encoding.

## v0 runtime

v0 is a single CLI process on an AWS EC2 G6 instance with an NVIDIA L4 GPU.

CUDA is required for inference. The program should fail clearly when the CUDA execution provider is unavailable rather than silently running the face model on CPU.

No API, queue, object storage, Cloudflare layer, or autoscaling belongs in v0.

## v0 pipeline

1. Validate 1–3 reference photos.
2. Probe target media with FFprobe.
3. Decode frames with FFmpeg / NVIDIA hardware acceleration where useful.
4. Detect and track the target face.
5. Build one identity representation from the reference photos.
6. Run the selected face-swap engine only on the relevant face crop.
7. Produce an occlusion/visibility mask and composite into the original frame.
8. Encode video with NVENC when available.
9. Copy/remux source audio rather than processing it.

## Long video policy

Do not chunk merely because a video is long. Stream frames through the worker when possible. Add fixed-duration chunks only when they improve bounded retries, memory use, or later parallel scheduling. Preserve codec settings and timestamps so concatenation does not force another quality-losing encode.

## Infrastructure

Start with one AWS G6/L4 worker and measure it.

Only after the CUDA CLI path is correct and benchmarked should we consider object storage, a queue, asynchronous APIs, scale-to-zero workers, or a Cloudflare edge.
