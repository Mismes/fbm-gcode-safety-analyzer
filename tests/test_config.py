from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from fbm_gcode_safety import ProfileError, load_profile

VALID = """\
[profile]
schema_version = 1
name = "test-machine"
units = "mm"
safe_rapid_z = 3.5

[rules]
require_spindle_for_cutting = true
require_feed_for_cutting = true
unknown_code = "warning"
"""


class ConfigTests(unittest.TestCase):
    def load(self, text: str):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "machine profile.toml"
            path.write_text(text, encoding="utf-8")
            return load_profile(path)

    def test_valid_profile_loads(self) -> None:
        profile = self.load(VALID)
        self.assertEqual("test-machine", profile.name)
        self.assertEqual(3.5, profile.safe_rapid_z)

    def test_missing_table_fails(self) -> None:
        with self.assertRaises(ProfileError):
            self.load("[profile]\nname='x'\n")

    def test_missing_value_fails(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace('name = "test-machine"\n', ""))

    def test_wrong_value_type_fails(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace("safe_rapid_z = 3.5", 'safe_rapid_z = "high"'))

    def test_boolean_is_not_accepted_as_number(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace("safe_rapid_z = 3.5", "safe_rapid_z = true"))

    def test_boolean_is_not_accepted_as_schema_version(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace("schema_version = 1", "schema_version = true"))

    def test_unknown_schema_fails(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace("schema_version = 1", "schema_version = 2"))

    def test_bad_units_fail(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace('units = "mm"', 'units = "cm"'))

    def test_bad_unknown_policy_fails(self) -> None:
        with self.assertRaises(ProfileError):
            self.load(VALID.replace('unknown_code = "warning"', 'unknown_code = "maybe"'))

    def test_missing_file_fails(self) -> None:
        with self.assertRaises(ProfileError):
            load_profile("does-not-exist.toml")


if __name__ == "__main__":
    unittest.main()
