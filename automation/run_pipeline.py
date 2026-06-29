#!/usr/bin/env python3
"""
Grant Analysis Pipeline - Single-command automation.

Chains the web crawler (index.py) and eligibility checker
(grant_eligibility_checker.py) into one unattended run.

Usage:
    python automation/run_pipeline.py                          # uses Grand_file.json
    python automation/run_pipeline.py --input path/to/file.json
    python automation/run_pipeline.py --input file.json --limit 10
    python automation/run_pipeline.py --all-statuses
"""

import argparse
import os
import subprocess
import sys
import time
from datetime import datetime

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

CRAWLER_SCRIPT = os.path.join(PROJECT_ROOT, "index.py")
CHECKER_SCRIPT = os.path.join(PROJECT_ROOT, "grant_eligibility_checker.py")
DEFAULT_INPUT = os.path.join(PROJECT_ROOT, "Grand_file.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "automation", "output")

PYTHON = sys.executable


def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {msg}")


def run_step(label: str, cmd: list[str]) -> subprocess.CompletedProcess:
    log(f"START  {label}")
    log(f"  CMD: {' '.join(cmd)}")
    start = time.time()

    result = subprocess.run(
        cmd,
        cwd=PROJECT_ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )

    elapsed = time.time() - start

    for line in result.stdout.splitlines():
        print(f"  | {line}")

    if result.returncode != 0:
        log(f"FAILED {label} (exit code {result.returncode}, {elapsed:.1f}s)")
        sys.exit(result.returncode)

    log(f"DONE   {label} ({elapsed:.1f}s)")
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Grant Analysis Pipeline - automated end-to-end run",
    )
    parser.add_argument(
        "--input",
        default=DEFAULT_INPUT,
        help=f"Input grants JSON file (default: Grand_file.json)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Analyse only the first N grants in the eligibility checker",
    )
    parser.add_argument(
        "--all-statuses",
        action="store_true",
        help="Analyse all grant statuses, not just Open",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Override the LLM model used by the eligibility checker",
    )
    parser.add_argument(
        "--skip-crawl",
        action="store_true",
        help="Skip the web-crawling step (use when input is already enriched)",
    )
    args = parser.parse_args()

    input_file = os.path.abspath(args.input)
    if not os.path.isfile(input_file):
        log(f"ERROR: Input file not found: {input_file}")
        sys.exit(1)

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawled_output = os.path.join(OUTPUT_DIR, f"crawled_grants_{ts}.json")

    pipeline_start = time.time()

    print("=" * 70)
    print("  GRANT ANALYSIS PIPELINE")
    print("=" * 70)
    print(f"  Input file  : {input_file}")
    print(f"  Skip crawl  : {args.skip_crawl}")
    print(f"  Output dir  : {OUTPUT_DIR}")
    print(f"  Started at  : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # ------------------------------------------------------------------
    # Step 1: Web crawling
    # ------------------------------------------------------------------
    if args.skip_crawl:
        log("SKIP   Web crawling (--skip-crawl flag set)")
        checker_input = input_file
    else:
        crawl_cmd = [
            PYTHON, CRAWLER_SCRIPT,
            input_file,
            "-o", crawled_output,
        ]
        run_step("Web Crawling (index.py)", crawl_cmd)

        if not os.path.isfile(crawled_output):
            log(f"ERROR: Crawler did not produce output file: {crawled_output}")
            sys.exit(1)

        checker_input = crawled_output

    # ------------------------------------------------------------------
    # Step 2: Eligibility analysis
    # ------------------------------------------------------------------
    checker_cmd = [
        PYTHON, CHECKER_SCRIPT,
        "--input", checker_input,
    ]
    if args.limit:
        checker_cmd += ["--limit", str(args.limit)]
    if args.all_statuses:
        checker_cmd += ["--all-statuses"]
    if args.model:
        checker_cmd += ["--model", args.model]

    run_step("Eligibility Analysis (grant_eligibility_checker.py)", checker_cmd)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    total_elapsed = time.time() - pipeline_start

    excel_files = sorted(
        [f for f in os.listdir(os.path.join(PROJECT_ROOT, "output"))
         if f.endswith(".xlsx")],
        key=lambda f: os.path.getmtime(
            os.path.join(PROJECT_ROOT, "output", f)
        ),
    )

    print("\n" + "=" * 70)
    print("  PIPELINE COMPLETE")
    print("=" * 70)
    if not args.skip_crawl:
        print(f"  Crawled data : {crawled_output}")
    if excel_files:
        latest_excel = os.path.join(PROJECT_ROOT, "output", excel_files[-1])
        print(f"  Excel report : {latest_excel}")
    print(f"  Total time   : {total_elapsed:.1f}s")
    print("=" * 70)


if __name__ == "__main__":
    main()
