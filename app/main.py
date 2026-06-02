import argparse
from typing import DefaultDict

from app.config import LAST_JOBS_MATCHES_PATH
from app.logging_config import setup_logging
from app.workflow import analyze_jobs, fetch_jobs, run_full_pipeline
from app.exporterss.export_xlsx import export_country_macthes_to_xlsx


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
    parser.add_argument(
        "--country", 
        choices=["ca", "nz", "usa", "gb"], 
        default="ca", 
        help="Country to export matches"
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
    commands.add_argument(
        "--export-xlsx", 
        action="store_true", 
        help="Export job to .xlsx file"
    )

    args = parser.parse_args()

    if args.fetch_jobs:
        print(f"Fetching jobs from {args.source}..")
        fetched_jobs, filtered_jobs = fetch_jobs(source=args.source)
        print(f"Fetched {len(fetched_jobs)} jobs, saved {len(filtered_jobs)} filtered jobs")

    elif args.analyze_jobs:
        print(f"Analyzing jobs against CV and preferences from {args.source}...")
        matches = analyze_jobs(source=args.source)
        print(f"Analyzed jobs and saved {len(matches)} matches to {LAST_JOBS_MATCHES_PATH}")

    elif args.run_pipeline:
        print(f"Running full pipeline: fetching and analyzing jobs for {args.source}...")
        result = run_full_pipeline(source=args.source)
        print(
            "Pipeline complete. "
            f"Fetched and analyzed jobs, saved {len(result.matches)} matches to {LAST_JOBS_MATCHES_PATH}, result is added to directory: data/matches/by_country"
        )

    elif args.export_xlsx:
        print(f"Exporting macthes from coutry {args.country} to xlsx...")
        export_country_macthes_to_xlsx(country=args.country)
        print("Matches exported to file!")

if __name__ == "__main__":
    main()