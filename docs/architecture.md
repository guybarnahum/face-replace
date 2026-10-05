# Architecture

## Principle

Keep identity replacement separate from media transport and infrastructure.

The expensive operation is per-frame face inference. Everything around it should minimize copies, redundant decoding, and re-encoding.

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

Do not chunk merely because a video is long. Stream frames through the worker when possible. Add fixed-duration chunks when they improve bounded retries or parallel scheduling. Preserve codec settings and timestamps so concatenation can occur without quality loss from another encode.

## Infrastructure

Start with one AWS G6/L4 worker. Add object storage and a queue when an external asynchronous API is needed. Scale-to-zero or ephemeral GPU workers are preferable to a permanently idle GPU for low-volume workloads.

Cloudflare may later handle ingress, API routing, result delivery, or R2 storage. It is not the primary arbitrary CUDA inference environment.
