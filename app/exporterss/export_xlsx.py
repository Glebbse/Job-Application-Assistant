from pathlib import Path
import json
from openpyxl import Workbook


# def decode_country(country: str) -> str:
#     countries = {
#         "ca": "canada", 
#         "gb": "great britain", 
#         "nz": "new zealand", 
#         "au": "australia", 
#         "usa": "usa"
#     }
#     for k, c in countries.items():
#         if country == k:
#             country = c
#     return country

def export_country_macthes_to_xlsx(*, country: str) -> None:
    # country = decode_country(_country)
    input_path = Path(f"data/matches/by_country/{country}.json")
    output_path = Path(f"exports/matches/by_country/{country}.xlsx")

    output_path.parent.mkdir(parents=True, exist_ok=True)

    matches = json.loads(input_path.read_text(encoding="utf-8"))

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = country.upper()

    headers = [
        "Title",
        "Company",
        "Location",
        "Source",
        "URL",
        "Recommendation",
        "Fit Score",
        "Interview Chance",
        "Keyword Score",
        "Strengths",
        "Gaps",
    ]

    sheet.append(headers)
    for match in matches:
        job = match["job"]
        ai = match["ai_analysis"]
        kw_analysis = match["keyword_analysis"]

        sheet.append([
            job.get("title"), 
            job.get("company"), 
            job.get("location"), 
            job.get("source"), 
            job.get("url"), 
            ai.get("recommendation"), 
            ai.get("fit_score"), 
            ai.get("interview_chance_score"), 
            kw_analysis.get("keyword_score"), 
        ])

    workbook.save(output_path)

