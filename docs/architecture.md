# Architecture

## Principle

Keep media orchestration independent from face-model implementations.

The expensive path is decode -> target face localization -> identity replacement -> composite -> encode. Provider/model glue belongs behind one small runtime contract so models can be compared without rewriting the media pipeline.

## Runtime selection

`config.yaml` selects the active runtime:

```yaml
runtime:
  provider: insightface
  model: inswapper_128
  device: cuda
  device_id: 0
  models_dir: models
```

Configuration chooses a provider and model at runtime; provider-specific implementation details stay in code, not in the media pipeline or CLI. `setup.sh` never reads `config.yaml`: setup installs supported provider integrations, while runtime configuration selects which installed provider/model is active.

## Contract

`FaceReplaceEngine` has two jobs:

1. fetch/validate the assets required by its configured model
2. prepare a reference identity and return a reusable `FaceReplaceSession`

`FaceReplaceSession.replace(frame)` performs replacement on one target frame.

This shape matters for video: the model and reference identity are prepared once, then the same session is reused for every decoded frame.

## Repository shape

```text
config.yaml
src/face_replace/
  config.py                 YAML -> validated runtime config
  runtime.py                tiny provider registry/factory
  engine/
    base.py                 provider-neutral contract
  providers/
    insightface/
      __init__.py           model dispatch for this provider
      inswapper.py          InSwapper-specific glue
  media/                    decode/probe/encode; never model-specific
  image.py                  current R2 image orchestration
```

Adding a model to an existing provider means adding its adapter and one dispatch entry. Adding a provider means adding one provider package and one registry entry. No dynamic plugin framework or inheritance hierarchy beyond the runtime contract.

## CUDA policy

v0 requires CUDA. Provider adapters must explicitly request CUDA and must not silently choose CPU. The current InsightFace adapter disables CPU execution-provider fallback.

## Model artifacts

Weights stay outside Git under `models/`. Each provider owns artifact download, cache layout, and integrity validation. Runtime configuration controls only the model cache root.

Model licenses are independent from this repository's code license. Evaluation models must not be assumed commercially licensed.

## Long-video direction

The media layer will eventually stream frames through one prepared session. Do not reload models or recompute reference identity per frame. Tracking is an R4 concern and should be added above or within the session without changing the media contract.