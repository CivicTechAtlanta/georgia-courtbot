import argparse
import datetime
import requests
import json
import sys
import csv
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.headers = {"User-Agent": "CodeForAtlanta Court Bot"}
        self.session = requests.Session()

    def get_all_judicial_officers(self):
        url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        result = [
            {"id": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSJudicialOfficer option")
        ]

        return filter(lambda e: e["name"] != "", result)

    def submit_search_by_judicial_officer(self, name, date_from, date_to):
        to_date_string = lambda d: datetime.date.strftime(d, "%m/%d/%Y")
        url = (
            "https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch"
        )

        data = {
            "PortletName": "HearingSearch",
            "Settings.CaptchaEnabled": "False",
            "Settings.DefaultLocation": "All Courts",
            "SearchCriteria.SelectedCourt": "All Courts",
            "SearchCriteria.SelectedHearingType": "All Hearings",
            "SearchCriteria.SearchByType": "JudicialOfficer",
            "SearchCriteria.SelectedJudicialOfficer": name,
            "SearchCriteria.DateFrom": to_date_string(date_from),
            "SearchCriteria.DateTo": to_date_string(date_to),
        }

        self.session.post(
            url,
            data=data,
            headers=self.headers,
        )

    def get_search_result(self):
        url = "https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read"
        data = {
            "sort": "",
            "group": "",
            "filter": "",
            "portletId": "27",
        }

        response = self.session.post(
            url,
            data=data,
            headers=self.headers,
        )

        return json.loads(response.content)

    def get_cases_by_judicial_officer(self, officer, date_from, date_to):
        log(f'{officer["id"]}\t{officer["name"]}')
        self.submit_search_by_judicial_officer(officer["id"], date_from, date_to)

        return self.get_search_result()["Data"]


def log(str):
    print(str, file=sys.stderr)


def write_json(results):
    print(json.dumps(results))


def write_csv(results):
    fieldnames = [
        "CaseId",
        "CaseNumber",
        "JudicialOfficer",
        "HearingDate",
        "HearingTime",
        "CourtRoom",
    ]
    writer = csv.DictWriter(sys.stdout, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(results)


def take_fields_of_interest(case):
    return {
        "CaseId": case["CaseId"],
        "CaseNumber": case["CaseNumber"],
        "HearingDate": case["HearingDate"],
        "HearingTime": case["HearingTime"],
        "CourtRoom": case["CourtRoom"],
    }


def run(output_format):
    scraper = Scraper()

    date_from = datetime.date.today()
    date_to = date_from + datetime.timedelta(days=90)

    results = []

    log("Scraping Dekalb County court cases per judicial officer...")
    log("ID\tName")

    for officer in scraper.get_all_judicial_officers():
        cases = scraper.get_cases_by_judicial_officer(officer, date_from, date_to)
        fields_of_interest = [take_fields_of_interest(case) for case in cases]
        fields_of_interest = [
            fields | {"JudicialOfficer": officer["name"]}
            for fields in fields_of_interest
        ]

        results.extend(fields_of_interest)

    log("Finished.")

    if output_format == "csv":
        write_csv(results)
        return
    if output_format == "json":
        write_json(results)

    print(f"Unknown output format: '{output_format}'!")


parser = argparse.ArgumentParser()
parser.add_argument(
    "--output", nargs="?", choices=["json", "csv"], help="Output format"
)

args = parser.parse_args()
if args.output is None:
    parser.print_help()
    sys.exit(1)

run(args.output)
