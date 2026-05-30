import argparse

from app.config import JOBS_MATCHES_PATH
from app.logging_config import setup_logging
from app.workflow import analyze_jobs, fetch_jobs, run_full_pipeline

def main():
    setup_logging()
    parser = argparse.ArgumentParser(description="Job Application Assistant")
    commands = parser.add_mutually_exclusive_group(required=True)
    parser.add_argument(
        "--source",
        choices=["remoteok", "remotive", "adzuna"],
        default="adzuna", 
        help="Job source to use"
    )
    commands.add_argument(
        "--fetch-jobs",
        action="store_true",
        help="Fetch jobs from API and save to JSON",
    )
    commands.add_argument(
        "--analyze-jobs",
        action="store_true",
        help="Analyze jobs against CV and preferences, save matches to JSON",
    )
    commands.add_argument(
        "--run-pipeline",
        action="store_true",
        help="Run full pipeline: fetch jobs and analyze them",
    )

    args = parser.parse_args()

    if args.fetch_jobs:
        print(f"Fetching jobs from {args.source}..")
        jobs = fetch_jobs(source=args.source)
        print(f"Fetched and saved {len(jobs)} jobs")

    elif args.analyze_jobs:
        print(f"Analyzing jobs against CV and preferences from {args.source}...")
        matches = analyze_jobs(source=args.source)
        print(f"Analyzed jobs and saved {len(matches)} matches to {JOBS_MATCHES_PATH}")

    elif args.run_pipeline:
        print(f"Running full pipeline: fetching and analyzing jobs for {args.source}...")
        matches = run_full_pipeline(source=args.source)
        print(
            "Pipeline complete. "
            f"Fetched and analyzed jobs, saved {len(matches)} matches to {JOBS_MATCHES_PATH}"
        )

if __name__ == "__main__":
    main()