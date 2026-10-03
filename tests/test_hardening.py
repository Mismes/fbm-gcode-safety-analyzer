"""Regression cases for conservative parsing, state, and batch output."""

import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from fbm_gcode_safety import analyze_file, analyze_text
from fbm_gcode_safety.cli import main
from fbm_gcode_safety.parser import parse_line
from fbm_gcode_safety.reporters import sarif


class HardeningTests(unittest.TestCase):
    def test_units_change_requires_new_feed(self):
        result = analyze_text("G21\nG90\nM3 S100\nG1 X1 F10\nG20\nG1 X2")
        self.assertTrue(any(d.rule == "GSA003" and d.line == 6 for d in result.diagnostics))

    def test_finite_numeric_conversion_overflow_is_rejected(self):
        result = analyze_text("G20\nG90\nG0 Z" + "1" + "0" * 307)
        self.assertEqual("failed", result.status)

    def test_comments_do_not_change_token_values(self):
        for value in range(-100, 101):
            plain, _ = parse_line(f"G1 X{value}.25 F20", 1)
            commented, errors = parse_line(f"G1 (S999 F999) X{value}.25 F20 ; M5", 1)
            self.assertFalse(errors)
            self.assertEqual(
                [(w.address, w.value) for w in plain.words],
                [(w.address, w.value) for w in commented.words],
            )

    def test_overflow_is_rejected(self):
        block, diagnostics = parse_line("G1 X" + "9" * 400, 1)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_duplicate_words_are_rejected(self):
        for address in ("X", "Y", "Z", "S", "F", "I", "R"):
            with self.subTest(address=address):
                block, diagnostics = parse_line(f"{address}1 {address}2", 1)
                self.assertIsNone(block)
                self.assertEqual("GSA004", diagnostics[0].rule)

    def test_comment_preserves_original_column(self):
        block, diagnostics = parse_line("(note) G1 X2", 1)
        self.assertFalse(diagnostics)
        self.assertEqual(8, block.words[0].column)

    def test_empty_or_comment_only_input_fails(self):
        for source in ("", "\n", "(comment)\n; comment\n", "%\nN10\n"):
            with self.subTest(source=source):
                self.assertEqual("failed", analyze_text(source).status)

    def test_conflicting_spindle_commands_fail(self):
        result = analyze_text("M3 M5 S100")
        self.assertIn("GSA004", [d.rule for d in result.diagnostics])

    def test_unknown_g_invalidates_following_motion(self):
        result = analyze_text("G21\nG90\nG0 Z5\nG10 X2\nX3")
        self.assertTrue(any(d.rule == "GSA006" and d.line == 5 for d in result.diagnostics))

    def test_unknown_m_invalidates_spindle_state(self):
        result = analyze_text("G21\nG90\nM3 S100\nG1 X1 F10\nM99\nG1 X2")
        self.assertTrue(any(d.rule == "GSA002" and d.line == 6 for d in result.diagnostics))

    def test_malformed_block_invalidates_position(self):
        result = analyze_text("G21\nG90\nG0 Z5\nZbad\nG21\nG91\nG0 Z1")
        self.assertTrue(any(d.rule == "GSA006" and d.line == 7 for d in result.diagnostics))

    def test_lateral_rapid_at_low_z_warns(self):
        result = analyze_text("G21\nG90\nG0 Z1\nX5")
        self.assertTrue(any(d.rule == "GSA001" and d.line == 4 for d in result.diagnostics))

    def test_lateral_rapid_at_unknown_z_fails(self):
        result = analyze_text("G21\nG90\nG0 X5")
        self.assertEqual("failed", result.status)

    def test_center_only_arc_checks_spindle_and_feed(self):
        result = analyze_text("G21\nG90\nG2 I1 J0")
        self.assertIn("GSA002", [d.rule for d in result.diagnostics])
        self.assertIn("GSA003", [d.rule for d in result.diagnostics])

    def test_bom_crlf_and_no_final_newline(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unicode 名.nc"
            path.write_bytes(b"\xef\xbb\xbfG21\r\nG90\r\nG0 Z5")
            self.assertEqual("passed", analyze_file(path).status)

    def test_sarif_relative_uri_escapes_spaces(self):
        result = analyze_text("G1 X2", source_name="examples/part file.nc")
        payload = json.loads(sarif.render(result))
        location = payload["runs"][0]["results"][0]["locations"][0]
        self.assertEqual(
            "examples/part%20file.nc", location["physicalLocation"]["artifactLocation"]["uri"]
        )

    def test_batch_outputs_are_single_documents(self):
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "safe.nc"
            second = Path(directory) / "unsafe.nc"
            first.write_text("G21\nG90\nG0 Z5", encoding="utf-8")
            second.write_text("G21\nG90\nG1 X2", encoding="utf-8")
            for output_format, field in (("json", "files"), ("sarif", "runs")):
                output = io.StringIO()
                with contextlib.redirect_stdout(output):
                    code = main([str(first), str(second), "--format", output_format])
                self.assertEqual(1, code)
                self.assertEqual(2, len(json.loads(output.getvalue())[field]))

    def test_action_empty_paths_and_unmatched_glob_fail(self):
        for paths in ("", "nonexistent/*.nc"):
            env = dict(os.environ, GSA_PATHS=paths, GSA_FORMAT="json", GSA_FAIL_ON="error")
            result = subprocess.run(
                [sys.executable, "action/run.py"], env=env, capture_output=True, text=True
            )
            self.assertEqual(2, result.returncode)

    def test_action_batch_json_is_single_document(self):
        env = dict(
            os.environ,
            GSA_PATHS="examples/safe.nc\nexamples/unsafe.nc",
            GSA_FORMAT="json",
            GSA_FAIL_ON="error",
            GSA_PROFILE="",
        )
        result = subprocess.run(
            [sys.executable, "action/run.py"], env=env, capture_output=True, text=True
        )
        self.assertEqual(1, result.returncode)
        self.assertEqual(2, len(json.loads(result.stdout)["files"]))
