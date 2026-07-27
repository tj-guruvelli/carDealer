#!/usr/bin/env python3
"""Out-the-door cost and weighted scoring for used-car candidates.

Listed price is not the price. This folds dealer fees, sales tax, and title/registration
into a single comparable number, then ranks candidates on weighted criteria.

Usage:
    python otd.py candidates.csv
    python otd.py candidates.csv --tax-rate 0.055 --title-fee 165
    python otd.py candidates.csv --weights price=0.4,reliability=0.3,mileage=0.2,history=0.1

Stdlib only. No network calls.
"""

import argparse
import csv
import sys

# Fields the scorer understands. Each maps to a column in the CSV.
#   price       - lower out-the-door is better
#   mileage     - lower is better
#   reliability - your 1-10 rating for the model/generation (from research, not vibes)
#   history     - your 1-10 rating for the Carfax/AutoCheck (owners, accidents, service gaps)
SCORED_FIELDS = ("price", "mileage", "reliability", "history")
LOWER_IS_BETTER = ("price", "mileage")

DEFAULT_WEIGHTS = {"price": 0.35, "reliability": 0.30, "history": 0.20, "mileage": 0.15}


def parse_weights(raw):
    """Parse 'price=0.4,reliability=0.3' into a normalized weight dict."""
    if not raw:
        return dict(DEFAULT_WEIGHTS)
    weights = {}
    for pair in raw.split(","):
        if "=" not in pair:
            raise ValueError("weight %r must look like field=number" % pair)
        field, value = pair.split("=", 1)
        field = field.strip()
        if field not in SCORED_FIELDS:
            raise ValueError(
                "unknown weight field %r; expected one of %s" % (field, ", ".join(SCORED_FIELDS))
            )
        weights[field] = float(value)
    total = sum(weights.values())
    if total <= 0:
        raise ValueError("weights must sum to a positive number")
    return {field: value / total for field, value in weights.items()}


def to_float(row, column, label, default=None):
    """Read a numeric column, failing loudly rather than silently zeroing."""
    raw = (row.get(column) or "").strip().replace("$", "").replace(",", "")
    if not raw:
        if default is None:
            raise ValueError("%s: column %r is required and was empty" % (label, column))
        return default
    try:
        return float(raw)
    except ValueError:
        raise ValueError("%s: column %r is not a number: %r" % (label, column, raw))


def out_the_door(row, label, tax_rate, title_fee):
    """price + dealer fees, taxed, plus title/registration.

    Sales tax is applied to price + dealer fee, which is how most US states treat a
    documentary fee. Verify against your own state's rule before trusting the total.
    """
    price = to_float(row, "price", label)
    dealer_fee = to_float(row, "dealer_fee", label, default=0.0)
    row_tax = row.get("tax_rate", "").strip()
    rate = float(row_tax) if row_tax else tax_rate
    taxable = price + dealer_fee
    return taxable + (taxable * rate) + title_fee


def normalize(values, lower_is_better):
    """Scale a list of numbers to 0..1, where 1 is always the best candidate."""
    low, high = min(values), max(values)
    if high == low:
        return [1.0] * len(values)
    span = high - low
    if lower_is_better:
        return [(high - v) / span for v in values]
    return [(v - low) / span for v in values]


def load_candidates(path, tax_rate, title_fee):
    with open(path, newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if not rows:
        raise ValueError("%s has no data rows" % path)

    candidates = []
    for index, row in enumerate(rows, start=2):  # start=2 accounts for the header line
        label = (row.get("name") or "").strip() or "row %d" % index
        candidates.append(
            {
                "name": label,
                "otd": out_the_door(row, label, tax_rate, title_fee),
                "mileage": to_float(row, "mileage", label),
                "reliability": to_float(row, "reliability", label),
                "history": to_float(row, "history", label),
            }
        )
    return candidates


def score(candidates, weights):
    columns = {
        "price": [c["otd"] for c in candidates],
        "mileage": [c["mileage"] for c in candidates],
        "reliability": [c["reliability"] for c in candidates],
        "history": [c["history"] for c in candidates],
    }
    normalized = {
        field: normalize(values, field in LOWER_IS_BETTER) for field, values in columns.items()
    }
    return [
        dict(candidate, score=sum(normalized[f][i] * weights.get(f, 0.0) for f in SCORED_FIELDS))
        for i, candidate in enumerate(candidates)
    ]


def render(scored):
    ranked = sorted(scored, key=lambda c: c["score"], reverse=True)
    width = max(len(c["name"]) for c in ranked)
    header = "%-*s  %12s  %9s  %6s" % (width, "CANDIDATE", "OUT-THE-DOOR", "MILES", "SCORE")
    lines = [header, "-" * len(header)]
    for candidate in ranked:
        lines.append(
            "%-*s  %12s  %9s  %6.3f"
            % (
                width,
                candidate["name"],
                "${:,.0f}".format(candidate["otd"]),
                "{:,.0f}".format(candidate["mileage"]),
                candidate["score"],
            )
        )
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("csv_path", help="candidates CSV (see candidates.example.csv)")
    parser.add_argument(
        "--tax-rate",
        type=float,
        required=True,
        help="combined state+local sales tax as a decimal, e.g. 0.0825. Look yours up; "
        "it varies by county and this number moves the total by hundreds of dollars.",
    )
    parser.add_argument(
        "--title-fee",
        type=float,
        default=0.0,
        help="flat title + registration cost for your state (default 0)",
    )
    parser.add_argument(
        "--weights",
        default="",
        help="comma-separated field=weight, e.g. price=0.4,reliability=0.3. "
        "Defaults to %s" % DEFAULT_WEIGHTS,
    )
    args = parser.parse_args(argv)

    try:
        weights = parse_weights(args.weights)
        candidates = load_candidates(args.csv_path, args.tax_rate, args.title_fee)
    except (ValueError, OSError) as error:
        print("error: %s" % error, file=sys.stderr)
        return 1

    print(render(score(candidates, weights)))
    print()
    print("Weights: %s" % ", ".join("%s=%.2f" % kv for kv in sorted(weights.items())))
    print("Score is relative to this candidate set only. Adding a car rescales everything.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
