from __future__ import annotations

import argparse
import sys

from .validation import ValidationError, validate_registry, validate_reviews


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Integration Harness research artifacts")
    parser.add_argument("registry", nargs="?", default="donors/registry.json")
    parser.add_argument("reviews", nargs="?", default="reviews")
    args = parser.parse_args()

    try:
        donors = validate_registry(args.registry)
        reviews = validate_reviews(args.reviews)
    except ValidationError as exc:
        print(f"validation failed: {exc}", file=sys.stderr)
        return 1

    print(f"validated {len(donors)} donor(s) and {len(reviews)} review artifact(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
