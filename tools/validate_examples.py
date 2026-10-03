"""Reproduce the public synthetic corpus through the installed CLI."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate() -> dict:
    manifest = json.loads((ROOT / "examples/validation/cases.json").read_text(encoding="utf-8"))
    checks = []
    for case in manifest["cases"]:
        expected = sorted(case["findings"])
        for output_format in ("json", "sarif"):
            for threshold in ("error", "warning", "never"):
                expected_exit = int(
                    threshold != "never"
                    and any(threshold == "warning" or f[1] == "error" for f in expected)
                )
                process = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "fbm_gcode_safety.cli",
                        case["path"],
                        "--profile",
                        manifest["profile"],
                        "--format",
                        output_format,
                        "--fail-on",
                        threshold,
                    ],
                    cwd=ROOT,
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                    timeout=30,
                )
                try:
                    payload = json.loads(process.stdout)
                    if output_format == "json":
                        observed = sorted(
                            [d["rule"], d["severity"], d["line"]] for d in payload["diagnostics"]
                        )
                        status_ok = payload["status"] == (
                            "failed" if any(f[1] == "error" for f in expected) else "passed"
                        )
                    else:
                        observed = sorted(
                            [
                                d["ruleId"],
                                d["level"],
                                d["locations"][0]["physicalLocation"]["region"]["startLine"],
                            ]
                            for d in payload["runs"][0]["results"]
                        )
                        status_ok = payload["version"] == "2.1.0"
                    passed = (
                        observed == expected
                        and process.returncode == expected_exit
                        and not process.stderr
                        and status_ok
                    )
                except (ValueError, KeyError, IndexError, TypeError):
                    passed = False
                checks.append(
                    {
                        "case": case["id"],
                        "format": output_format,
                        "threshold": threshold,
                        "passed": passed,
                        "expected_exit": expected_exit,
                        "actual_exit": process.returncode,
                    }
                )
    return {
        "corpus": "synthetic bounded contract; not machine validation",
        "cases": len(manifest["cases"]),
        "checks": len(checks),
        "passed": sum(check["passed"] for check in checks),
        "failures": [check for check in checks if not check["passed"]],
    }


if __name__ == "__main__":
    report = validate()
    print(json.dumps(report, indent=2))
    raise SystemExit(bool(report["failures"]))
