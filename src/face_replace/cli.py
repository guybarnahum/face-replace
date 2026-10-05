from __future__ import annotations

import argparse
from pathlib import Path

from face_replace.media.probe import probe


def main() -> None:
    parser = argparse.ArgumentParser(prog="face-replace")
    subparsers = parser.add_subparsers(dest="command", required=True)

    probe_parser = subparsers.add_parser("probe", help="Inspect target media")
    probe_parser.add_argument("media", type=Path)

    args = parser.parse_args()
    if args.command == "probe":
        print(probe(args.media))


if __name__ == "__main__":
    main()
