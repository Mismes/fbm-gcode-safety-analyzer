"""Command-line interface."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .analyzer import analyze_file
from .config import ProfileError, default_profile, load_profile
from .reporters import console, sarif
from .reporters import json as json_reporter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fbm-gcode-check",
        description="Statically check a bounded Fanuc-style G-code subset.",
    )
    parser.add_argument("path", type=Path, help="G-code file to analyze")
    parser.add_argument("--profile", type=Path, help="version 1 TOML machine profile")
    parser.add_argument(
        "--format", choices=("console", "json", "sarif"), default="console", dest="output_format"
    )
    parser.add_argument(
        "--fail-on",
        choices=("error", "warning", "never"),
        default="error",
        help="finding severity that produces exit code 1 (default: error)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        profile = load_profile(args.profile) if args.profile else default_profile()
        result = analyze_file(args.path, profile)
    except (OSError, UnicodeError, ProfileError) as exc:
        print(f"fbm-gcode-check: {exc}", file=sys.stderr)
        return 2

    reporters = {"console": console.render, "json": json_reporter.render, "sarif": sarif.render}
    output = reporters[args.output_format](result)
    if output:
        print(output)
    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning":
        return 1 if result.diagnostics else 0
    return 1 if result.status == "failed" else 0


if __name__ == "__main__":
    raise SystemExit(main())
