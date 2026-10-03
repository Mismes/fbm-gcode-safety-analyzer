from __future__ import annotations

import unittest

from fbm_gcode_safety.parser import parse_line, parse_text


class ParserTests(unittest.TestCase):
    def test_blank_line_returns_empty_block(self) -> None:
        block, diagnostics = parse_line("   ", 4)
        self.assertEqual([], diagnostics)
        self.assertIsNotNone(block)
        self.assertEqual((), block.words)

    def test_percent_delimiter_returns_empty_block(self) -> None:
        block, diagnostics = parse_line("%", 1)
        self.assertEqual([], diagnostics)
        self.assertEqual((), block.words)

    def test_lowercase_and_line_number_are_tokenized(self) -> None:
        block, diagnostics = parse_line("n10 g01 x-1.25 f.5", 2)
        self.assertEqual([], diagnostics)
        self.assertEqual(["N", "G", "X", "F"], [word.address for word in block.words])
        self.assertEqual(-1.25, block.words[2].value)
        self.assertEqual(0.5, block.words[3].value)

    def test_parenthesized_comment_is_removed(self) -> None:
        block, diagnostics = parse_line("G1 (S1000) X2", 1)
        self.assertEqual([], diagnostics)
        self.assertEqual(["G", "X"], [word.address for word in block.words])

    def test_semicolon_comment_is_removed(self) -> None:
        block, diagnostics = parse_line("G1 X2 ; S1000", 1)
        self.assertEqual([], diagnostics)
        self.assertEqual(["G", "X"], [word.address for word in block.words])

    def test_unclosed_comment_is_malformed(self) -> None:
        block, diagnostics = parse_line("G1 (oops", 3)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_unmatched_closing_comment_is_malformed(self) -> None:
        block, diagnostics = parse_line("G1 ) X2", 3)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_nested_comment_is_malformed(self) -> None:
        block, diagnostics = parse_line("G1 (a (b)) X2", 3)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_word_without_number_is_malformed(self) -> None:
        block, diagnostics = parse_line("G X2", 5)
        self.assertIsNone(block)
        self.assertIn("no valid numeric", diagnostics[0].message)

    def test_unexpected_character_is_malformed(self) -> None:
        block, diagnostics = parse_line("G1 #2", 5)
        self.assertIsNone(block)
        self.assertEqual(4, diagnostics[0].column)

    def test_g10_remains_one_exact_word(self) -> None:
        block, diagnostics = parse_line("G10 X5", 1)
        self.assertEqual([], diagnostics)
        self.assertEqual(10, block.words[0].code())

    def test_fractional_line_number_is_malformed(self) -> None:
        block, diagnostics = parse_line("N1.5 G1 X2", 1)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_line_number_after_command_is_malformed(self) -> None:
        block, diagnostics = parse_line("G1 N10 X2", 1)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_multiple_line_numbers_are_malformed(self) -> None:
        block, diagnostics = parse_line("N10 N20 G1 X2", 1)
        self.assertIsNone(block)
        self.assertEqual("GSA004", diagnostics[0].rule)

    def test_parse_text_preserves_line_numbers(self) -> None:
        blocks, diagnostics = parse_text("\nG21\nG90\n")
        self.assertEqual([], diagnostics)
        self.assertEqual([1, 2, 3], [block.line for block in blocks])


if __name__ == "__main__":
    unittest.main()
