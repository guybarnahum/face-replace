from __future__ import annotations

import argparse
from pathlib import Path

from face_replace.config import ConfigError, load_config
from face_replace.doctor import print_doctor
from face_replace.engine.base import FaceReplaceError
from face_replace.image import replace_image
from face_replace.media.probe import probe
from face_replace.runtime import RuntimeConfigError, create_engine


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="face-replace")
    parser.add_argument(
        "--config",
        type=Path,
        default=Path("config.yaml"),
        help="Runtime configuration (default: config.yaml)",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check the CUDA media runtime")

    probe_parser = subparsers.add_parser("probe", help="Inspect target media")
    probe_parser.add_argument("media", type=Path)

    models_parser = subparsers.add_parser(
        "models",
        help="Manage assets for the configured model",
    )
    model_commands = models_parser.add_subparsers(
        dest="models_command",
        required=True,
    )
    model_commands.add_parser(
        "fetch",
        help="Fetch assets required by the configured model",
    )

    swap_parser = subparsers.add_parser(
        "swap",
        help="Replace a face in one image",
    )
    swap_parser.add_argument(
        "--reference",
        type=Path,
        action="append",
        required=True,
        help="Reference face image; repeatable for models that support it",
    )
    swap_parser.add_argument("--target", type=Path, required=True)
    swap_parser.add_argument("--output", type=Path, required=True)

    return parser


def main() -> None:
    args = _parser().parse_args()

    if args.command == "doctor":
        raise SystemExit(0 if print_doctor() else 1)

    if args.command == "probe":
        print(probe(args.media))
        return

    try:
        config = load_config(args.config)
        engine = create_engine(config.runtime)

        if args.command == "models":
            artifacts = engine.fetch_assets()
            print(f"{config.runtime.provider}/{config.runtime.model}")
            for artifact in artifacts:
                print(f"  ✓ {artifact}")
            return

        if args.command == "swap":
            result = replace_image(
                engine,
                references=args.reference,
                target=args.target,
                output=args.output,
            )
            print(
                f"{config.runtime.provider}/{config.runtime.model} · "
                f"prepare {result.prepare_seconds:.2f}s · "
                f"replace {result.replace_seconds:.2f}s"
            )
            print(result.output)
            return

    except (ConfigError, RuntimeConfigError, FaceReplaceError) as exc:
        raise SystemExit(f"error: {exc}") from exc


if __name__ == "__main__":
    main()
