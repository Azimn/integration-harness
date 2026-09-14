from __future__ import annotations

import argparse
import sys

from .validation import (
    ValidationError,
    validate_registry,
    validate_review_gate,
    validate_reviews,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Integration Harness research artifacts")
    parser.add_argument("registry", nargs="?", default="donors/registry.json")
    parser.add_argument("reviews", nargs="?", default="reviews")
    parser.add_argument(
        "--require-review-gate",
        action="store_true",
        help="require a passing review that covers the latest substantive repository state",
    )
    parser.add_argument(
        "--head",
        default="HEAD",
        help="git revision treated as the current head when review-gate validation is enabled",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="repository root used for git ancestry and diff checks",
    )
    args = parser.parse_args()

    try:
        donors = validate_registry(args.registry)
        reviews = validate_reviews(args.reviews)
        gate = None
        if args.require_review_gate:
            gate = validate_review_gate(args.reviews, args.head, args.repo_root)
    except ValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    message = f"validated {len(donors)} donor(s) and {len(reviews)} review artifact(s)"
    if gate:
        message += f"; review gate covered by {gate}"
    print(message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
