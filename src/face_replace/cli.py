from __future__ import annotations

import argparse
from pathlib import Path

from face_replace.config import load_config
from face_replace.doctor import print_doctor
from face_replace.image import replace_image
from face_replace.media.probe import probe
from face_replace.runtime import create_engine


def main() -> None:
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

    models_parser = subparsers.add_parser("models", help="Manage model artifacts")
    model_commands = models_parser.add_subparsers(dest="models_command", required=True)
    model_commands.add_parser("fetch", help="Fetch models for configured runtime")

    swap_parser = subparsers.add_parser("swap", help="Replace a face in one image")
    swap_parser.add_argument(
        "--reference",
        type=Path,
        action="append",
        required=True,
        help="Reference face image; repeatable for engines that support it",
    )
    swap_parser.add_argument("--target", type=Path, required=True)
    swap_parser.add_argument("--output", type=Path, required=True)

    args = parser.parse_args()

    if args.command == "doctor":
        raise SystemExit(0 if print_doctor() else 1)

    if args.command == "probe":
        print(probe(args.media))
        return

    config = load_config(args.config)
    engine = create_engine(config.runtime)

    if args.command == "models":
        artifacts = engine.fetch_models()
        for artifact in artifacts:
            print(artifact)
        return

    if args.command == "swap":
        output = replace_image(
            engine,
            references=args.reference,
            target=args.target,
            output=args.output,
        )
        print(output)


if __name__ == "__main__":
    main()
