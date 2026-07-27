"""Behavior tests for otd.py.

These exercise the module through the interfaces a caller actually uses:
load_candidates / score / render / main. They describe what the tool does with a
CSV and a tax rate, not how it does it internally.
"""

import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import otd


def write_csv(text):
    """Write a CSV to a temp file and return its path."""
    handle = tempfile.NamedTemporaryFile(
        "w", suffix=".csv", delete=False, newline="", encoding="utf-8"
    )
    handle.write(text)
    handle.close()
    return handle.name


HEADER = "name,price,dealer_fee,tax_rate,mileage,reliability,history\n"


class OutTheDoorMath(unittest.TestCase):
    def test_folds_dealer_fee_into_the_taxable_amount(self):
        """Tax applies to price + dealer fee, then title is added untaxed."""
        path = write_csv(HEADER + "A,20000,1000,,50000,8,8\n")
        candidates = otd.load_candidates(path, tax_rate=0.10, title_fee=165)
        # (20000 + 1000) * 1.10 + 165
        self.assertAlmostEqual(candidates[0]["otd"], 23265.0, places=2)

    def test_a_cheaper_sticker_can_lose_to_a_lower_fee_car(self):
        """The whole point of the tool: sticker price is not the price."""
        path = write_csv(HEADER + "cheap-sticker,20000,2000,,50000,8,8\n"
                         + "higher-sticker,20500,500,,50000,8,8\n")
        by_name = {c["name"]: c["otd"] for c in otd.load_candidates(path, 0.08, 0)}
        self.assertGreater(by_name["cheap-sticker"], by_name["higher-sticker"])

    def test_per_row_tax_rate_overrides_the_command_line_rate(self):
        """A car in another county carries its own rate."""
        path = write_csv(HEADER + "A,10000,0,0.05,50000,8,8\n")
        candidates = otd.load_candidates(path, tax_rate=0.99, title_fee=0)
        self.assertAlmostEqual(candidates[0]["otd"], 10500.0, places=2)

    def test_blank_dealer_fee_is_treated_as_zero(self):
        path = write_csv("name,price,mileage,reliability,history\nA,10000,50000,8,8\n")
        candidates = otd.load_candidates(path, tax_rate=0.0, title_fee=0)
        self.assertAlmostEqual(candidates[0]["otd"], 10000.0, places=2)

    def test_currency_formatting_in_the_csv_is_accepted(self):
        """People paste '$27,990' out of a listing."""
        path = write_csv(HEADER + 'A,"$27,990",0,,50000,8,8\n')
        candidates = otd.load_candidates(path, tax_rate=0.0, title_fee=0)
        self.assertAlmostEqual(candidates[0]["otd"], 27990.0, places=2)


class MalformedInput(unittest.TestCase):
    def test_missing_required_value_raises_instead_of_scoring_as_zero(self):
        """A blank price must never silently become the best deal."""
        path = write_csv(HEADER + "A,,0,,50000,8,8\n")
        with self.assertRaises(ValueError) as caught:
            otd.load_candidates(path, 0.08, 0)
        self.assertIn("price", str(caught.exception))

    def test_non_numeric_value_names_the_row_and_column(self):
        path = write_csv(HEADER + "Blue Jag,abc,0,,50000,8,8\n")
        with self.assertRaises(ValueError) as caught:
            otd.load_candidates(path, 0.08, 0)
        message = str(caught.exception)
        self.assertIn("Blue Jag", message)
        self.assertIn("price", message)

    def test_short_row_does_not_crash(self):
        """A row with fewer fields than the header leaves trailing columns as None."""
        path = write_csv(HEADER + "A,10000,0\n")
        with self.assertRaises(ValueError):
            otd.load_candidates(path, 0.08, 0)

    def test_empty_csv_is_rejected(self):
        path = write_csv(HEADER)
        with self.assertRaises(ValueError):
            otd.load_candidates(path, 0.08, 0)


class Scoring(unittest.TestCase):
    def test_cheaper_and_lower_mileage_scores_higher(self):
        path = write_csv(HEADER + "good,10000,0,,10000,9,9\n" + "bad,40000,0,,150000,3,3\n")
        scored = {c["name"]: c["score"] for c in otd.score(
            otd.load_candidates(path, 0.0, 0), otd.DEFAULT_WEIGHTS)}
        self.assertGreater(scored["good"], scored["bad"])

    def test_identical_candidates_do_not_divide_by_zero(self):
        path = write_csv(HEADER + "A,10000,0,,50000,8,8\n" + "B,10000,0,,50000,8,8\n")
        scored = otd.score(otd.load_candidates(path, 0.0, 0), otd.DEFAULT_WEIGHTS)
        self.assertEqual(scored[0]["score"], scored[1]["score"])

    def test_weights_are_normalized_so_only_ratios_matter(self):
        doubled = otd.parse_weights("price=2,reliability=2,history=2,mileage=2")
        self.assertAlmostEqual(sum(doubled.values()), 1.0, places=6)
        for value in doubled.values():
            self.assertAlmostEqual(value, 0.25, places=6)

    def test_unknown_weight_field_is_rejected(self):
        with self.assertRaises(ValueError):
            otd.parse_weights("colour=1")

    def test_zero_total_weight_is_rejected(self):
        with self.assertRaises(ValueError):
            otd.parse_weights("price=0,mileage=0")


class CommandLine(unittest.TestCase):
    def test_ranks_best_first_and_reports_weights(self):
        path = write_csv(HEADER + "winner,10000,0,,10000,9,9\n" + "loser,40000,0,,150000,3,3\n")
        out = io.StringIO()
        with redirect_stdout(out):
            code = otd.main([path, "--tax-rate", "0.08"])
        self.assertEqual(code, 0)
        lines = out.getvalue().splitlines()
        rows = [l for l in lines if l.startswith(("winner", "loser"))]
        self.assertTrue(rows[0].startswith("winner"))
        self.assertIn("Weights:", out.getvalue())

    def test_bad_file_exits_nonzero_with_a_message_on_stderr(self):
        err = io.StringIO()
        with redirect_stderr(err):
            code = otd.main(["definitely-not-a-file.csv", "--tax-rate", "0.08"])
        self.assertEqual(code, 1)
        self.assertIn("error", err.getvalue())


if __name__ == "__main__":
    unittest.main(verbosity=2)
