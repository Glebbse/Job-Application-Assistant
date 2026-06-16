import argparse

from app.logging_config import setup_logging
from app.workflow import run_full_pipeline
from app.exporters.export_xlsx import export_country_macthes_to_xlsx


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
        choices=["ca", "nz", "us", "gb", "au", "multi"], 
        default="ca", 
        help="Country to export matches"
    )

    # commands.add_argument(
    #     "--fetch-jobs",
    #     action="store_true",
    #     help="Fetch jobs from API and save to JSON",
    # )
    # commands.add_argument(
    #     "--analyze-jobs",
    #     action="store_true",
    #     help="Analyze jobs against CV and preferences, save matches to JSON",
    # )
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

    if args.run_pipeline:
        print(f"Running full pipeline: fetching and analyzing jobs for {args.source}...")
        result = run_full_pipeline(source=args.source, country=args.country)
        print(
            "Pipeline complete. "
            f"Fetched and analyzed jobs, saved results to directory: data/matches/by_country"
        )

    elif args.export_xlsx:
        print(f"Exporting macthes from coutry {args.country} to xlsx...")
        export_country_macthes_to_xlsx(country=args.country)
        print("Matches exported to file!")

if __name__ == "__main__":
    main()