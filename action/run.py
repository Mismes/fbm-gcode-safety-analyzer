"""Portable entry point for the composite GitHub Action."""

from __future__ import annotations

import os
from glob import glob

from fbm_gcode_safety.cli import main

patterns = [line.strip() for line in os.environ["GSA_PATHS"].splitlines() if line.strip()]
paths = [match for pattern in patterns for match in (glob(pattern, recursive=True) or [pattern])]
exit_code = 0
for path in paths:
    arguments = [
        path,
        "--format",
        os.environ["GSA_FORMAT"],
        "--fail-on",
        os.environ["GSA_FAIL_ON"],
    ]
    if os.environ.get("GSA_PROFILE"):
        arguments.extend(["--profile", os.environ["GSA_PROFILE"]])
    exit_code = max(exit_code, main(arguments))
raise SystemExit(exit_code)
