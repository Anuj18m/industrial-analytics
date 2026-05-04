#!/usr/bin/env python3
"""
generate_github_report.py
=========================
CLI script that fetches public GitHub data for a given username and writes a
structured, fact-based markdown analysis report.

Usage
-----
    python generate_github_report.py                         # defaults to Anuj18m
    python generate_github_report.py --username some_user
    python generate_github_report.py --username Anuj18m --output my_report.md
    python generate_github_report.py --print                 # print to stdout instead
"""

import argparse
import sys
from pathlib import Path

from github_profile.analyzer import fetch_profile
from github_profile.report_generator import generate_report


DEFAULT_USERNAME = "Anuj18m"
DEFAULT_OUTPUT = "github_profile_analysis.md"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a GitHub profile analysis report."
    )
    parser.add_argument(
        "--username",
        default=DEFAULT_USERNAME,
        help=f"GitHub username to analyse (default: {DEFAULT_USERNAME})",
    )
    parser.add_argument(
        "--output",
        default=DEFAULT_OUTPUT,
        help=f"Output file path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--print",
        dest="print_only",
        action="store_true",
        help="Print the report to stdout instead of saving to a file",
    )
    args = parser.parse_args()

    print(f"🔍 Fetching public GitHub data for @{args.username} …", file=sys.stderr)
    profile = fetch_profile(args.username)

    if not profile.get("repos"):
        print(
            f"⚠️  No public repositories found for @{args.username}. "
            "Check the username or your network connection.",
            file=sys.stderr,
        )

    print("📝 Generating report …", file=sys.stderr)
    report = generate_report(profile)

    if args.print_only:
        print(report)
    else:
        output_path = Path(args.output)
        output_path.write_text(report, encoding="utf-8")
        print(f"✅ Report saved to: {output_path.resolve()}", file=sys.stderr)


if __name__ == "__main__":
    main()
