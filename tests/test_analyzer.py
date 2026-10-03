from __future__ import annotations

import unittest
from dataclasses import replace

from fbm_gcode_safety import analyze_text, default_profile


def rules(source: str, profile=None) -> list[str]:
    return [item.rule for item in analyze_text(source, profile).diagnostics]


class AnalyzerTests(unittest.TestCase):
    def test_safe_modal_cutting_sequence_passes(self) -> None:
        source = "G21\nG90\nM3 S1200\nG1 X10 F200\nG1 X20\n"
        self.assertEqual([], rules(source))

    def test_comment_does_not_set_spindle_speed(self) -> None:
        source = "G21\nG90\nM3\n(COMMENT WITH S1000)\nG1 X10 F200\n"
        self.assertIn("GSA002", rules(source))

    def test_g10_is_unsupported_not_cutting(self) -> None:
        result = analyze_text("G10 X5\n")
        self.assertEqual(["GSA005"], [item.rule for item in result.diagnostics])

    def test_g10_does_not_inherit_prior_g1_motion(self) -> None:
        source = "G21\nG90\nM3 S1200\nG1 X1 F20\nM5\nG10 X5\n"
        self.assertEqual(["GSA005"], rules(source))

    def test_spindle_stop_is_modal(self) -> None:
        source = "G21\nG90\nM3 S1200\nG1 X1 F20\nM5\nG1 X2\n"
        self.assertEqual(["GSA002"], rules(source))

    def test_missing_feed_is_error(self) -> None:
        source = "G21\nG90\nM3 S1200\nG1 X1\n"
        self.assertIn("GSA003", rules(source))

    def test_zero_feed_is_invalid(self) -> None:
        source = "G21\nG90\nM3 S1200\nG1 X1 F0\n"
        self.assertIn("GSA003", rules(source))

    def test_zero_spindle_speed_is_invalid(self) -> None:
        source = "G21\nG90\nM3 S0\nG1 X1 F20\n"
        self.assertIn("GSA002", rules(source))

    def test_rapid_below_clearance_warns(self) -> None:
        source = "G21\nG90\nG0 Z1.5\n"
        result = analyze_text(source)
        self.assertEqual(["GSA001"], [item.rule for item in result.diagnostics])
        self.assertEqual("passed", result.status)

    def test_rapid_at_clearance_passes(self) -> None:
        self.assertEqual([], rules("G21\nG90\nG0 Z2\n"))

    def test_inch_rapid_is_converted_to_profile_units(self) -> None:
        self.assertIn("GSA001", rules("G20\nG90\nG0 Z0.05\n"))

    def test_known_incremental_position_is_applied(self) -> None:
        source = "G21\nG90\nG0 Z5\nG91\nG0 Z-4\n"
        self.assertIn("GSA001", rules(source))

    def test_unknown_incremental_start_is_error(self) -> None:
        source = "G21\nG91\nG0 Z1\n"
        self.assertIn("GSA006", rules(source))

    def test_missing_units_is_error(self) -> None:
        self.assertIn("GSA006", rules("G90\nG0 Z5\n"))

    def test_missing_positioning_is_error(self) -> None:
        self.assertIn("GSA006", rules("G21\nG0 Z5\n"))

    def test_conflicting_units_are_error(self) -> None:
        self.assertIn("GSA006", rules("G20 G21\n"))

    def test_conflicting_positioning_modes_are_error(self) -> None:
        self.assertIn("GSA006", rules("G90 G91\n"))

    def test_conflicting_motion_modes_are_malformed(self) -> None:
        self.assertIn("GSA004", rules("G0 G1 X2\n"))

    def test_mode_change_on_motion_block_warns(self) -> None:
        self.assertIn("GSA006", rules("G21\nG90 G0 Z5\n"))

    def test_unknown_policy_can_be_error(self) -> None:
        profile = replace(default_profile(), unknown_code="error")
        result = analyze_text("G10\n", profile)
        self.assertEqual("error", result.diagnostics[0].severity.value)

    def test_unknown_policy_can_ignore(self) -> None:
        profile = replace(default_profile(), unknown_code="ignore")
        self.assertEqual([], rules("G10\n", profile))

    def test_spindle_requirement_can_be_disabled(self) -> None:
        profile = replace(default_profile(), require_spindle_for_cutting=False)
        source = "G21\nG90\nG1 X1 F20\n"
        self.assertNotIn("GSA002", rules(source, profile))

    def test_feed_requirement_can_be_disabled(self) -> None:
        profile = replace(default_profile(), require_feed_for_cutting=False)
        source = "G21\nG90\nM3 S100\nG1 X1\n"
        self.assertNotIn("GSA003", rules(source, profile))


if __name__ == "__main__":
    unittest.main()
