from __future__ import annotations

import argparse
from pathlib import Path

from face_replace.doctor import print_doctor
from face_replace.media.probe import probe


def main() -> None:
    parser = argparse.ArgumentParser(prog="face-replace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Check the CUDA media runtime")

    probe_parser = subparsers.add_parser("probe", help="Inspect target media")
    probe_parser.add_argument("media", type=Path)

    args = parser.parse_args()

    if args.command == "doctor":
        raise SystemExit(0 if print_doctor() else 1)

    if args.command == "probe":
        print(probe(args.media))


if __name__ == "__main__":
    main()
