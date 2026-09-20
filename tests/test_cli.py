from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path

from fbm_gcode_safety.cli import main


class CliTests(unittest.TestCase):
    def run_cli(self, source: str, *arguments: str) -> tuple[int, str, str]:
        with tempfile.TemporaryDirectory(prefix="gsa path ") as directory:
            path = Path(directory) / "part file.nc"
            path.write_text(source, encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                code = main([str(path), *arguments])
        return code, stdout.getvalue(), stderr.getvalue()

    def test_safe_input_returns_zero(self) -> None:
        code, output, error = self.run_cli("G21\nG90\nM3 S100\nG1 X1 F10\n")
        self.assertEqual(0, code)
        self.assertEqual("", output)
        self.assertEqual("", error)

    def test_error_finding_returns_one(self) -> None:
        code, output, _ = self.run_cli("G21\nG90\nG1 X1\n")
        self.assertEqual(1, code)
        self.assertIn("GSA002 ERROR", output)

    def test_warning_only_returns_zero(self) -> None:
        code, output, _ = self.run_cli("G21\nG90\nG0 Z1\n")
        self.assertEqual(0, code)
        self.assertIn("GSA001 WARNING", output)

    def test_json_output_has_documented_shape(self) -> None:
        code, output, _ = self.run_cli("G21\nG90\nG1 X1\n", "--format", "json")
        payload = json.loads(output)
        self.assertEqual(1, code)
        self.assertEqual("failed", payload["status"])
        self.assertIn("rule", payload["diagnostics"][0])
        self.assertIn("severity", payload["diagnostics"][0])
        self.assertIn("line", payload["diagnostics"][0])
        self.assertIn("message", payload["diagnostics"][0])

    def test_missing_input_returns_two(self) -> None:
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(["missing file.nc"])
        self.assertEqual(2, code)
        self.assertIn("fbm-gcode-check:", stderr.getvalue())

    def test_warning_threshold_can_fail(self) -> None:
        code, _, _ = self.run_cli("G21\nG90\nG0 Z1\n", "--fail-on", "warning")
        self.assertEqual(1, code)

    def test_never_threshold_does_not_fail(self) -> None:
        code, _, _ = self.run_cli("G21\nG90\nG1 X1\n", "--fail-on", "never")
        self.assertEqual(0, code)

    def test_sarif_output_has_required_structure(self) -> None:
        code, output, _ = self.run_cli("G21\nG90\nG1 X1\n", "--format", "sarif")
        payload = json.loads(output)
        self.assertEqual(1, code)
        self.assertEqual("2.1.0", payload["version"])
        run = payload["runs"][0]
        self.assertEqual("FBM G-code Safety Analyzer", run["tool"]["driver"]["name"])
        self.assertEqual("GSA002", run["results"][0]["ruleId"])
        region = run["results"][0]["locations"][0]["physicalLocation"]["region"]
        self.assertEqual(3, region["startLine"])


if __name__ == "__main__":
    unittest.main()
