import datetime
import requests
import json
import sys
import csv
import jsonschema
import os
from bs4 import BeautifulSoup


class Scraper:
    def __init__(self):
        self.headers = {"User-Agent": "CodeForAtlanta Court Bot"}
        self.session = requests.Session()

    def close_session(self):
        self.session.close()

    def get_all_judicial_officers(self):
        url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
        response = self.session.get(url, headers=self.headers)
        cache("cached/get_all_judicial_officers", response.content)
        soup = BeautifulSoup(response.content, "html.parser")

        result = [
            {"id": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSJudicialOfficer option")
        ]

        return filter(lambda e: e["name"] != "", result)

    def search_by_judicial_officer(self, name, date_from, date_to):
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
            "SearchCriteria.DateFrom": datetime_to_hearing_date(date_from),
            "SearchCriteria.DateTo": datetime_to_hearing_date(date_to),
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

        cache(f"cached/get_search_result_{datetime.datetime.now()}", response.content)
        return json.loads(response.content)

    def get_cases_by_judicial_officer(self, officer, date_from, date_to):
        self.search_by_judicial_officer(officer["id"], date_from, date_to)
        response = self.get_search_result()
        cases = response["Data"]
        if response["MaxResultsHit"] == True:
            last_case = max(
                cases, key=lambda case: hearing_date_to_datetime(case["HearingDate"])
            )
            offset_date_from = hearing_date_to_datetime(last_case["HearingDate"])
            page = self.get_cases_by_judicial_officer(
                officer, offset_date_from, date_to
            )
            cases.extend(case for case in page if case not in cases)

        return cases


def hearing_date_to_datetime(string):
    return datetime.datetime.strptime(string, "%m/%d/%Y")


def datetime_to_hearing_date(dt):
    return datetime.date.strftime(dt, "%m/%d/%Y")


def cache(filepath, content):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "wb+") as f:
        f.write(content)


def log(*args):
    for arg in args:
        print(arg, file=sys.stderr)


def take_fields_of_interest(case):
    return {
        "CaseId": case["CaseId"],
        "CaseNumber": case["CaseNumber"],
        "HearingDate": case["HearingDate"],
        "HearingTime": case["HearingTime"],
        "CourtRoom": case["CourtRoom"],
        "JudicialOfficer": case["JudgeParsed"],
    }


def scrape(days):
    scraper = Scraper()

    date_from = datetime.date.today()
    date_to = date_from + datetime.timedelta(days)

    results = []

    log(
        f"Scraping Dekalb County court cases per judicial officer from {date_from} to {date_to}.",
        f"---",
        f"ID\tName\t",
    )

    for officer in scraper.get_all_judicial_officers():
        log(f'{officer["id"]}\t{officer["name"]}')
        cases = scraper.get_cases_by_judicial_officer(officer, date_from, date_to)
        results.extend([take_fields_of_interest(case) for case in cases])

    return results


def validate(results):
    schema_file_path = os.path.join(os.path.dirname(__file__), "schema", "case.json")
    schema = json.load(open(schema_file_path))
    for case in results:
        jsonschema.validate(instance=case, schema=schema)


def report(results, output_format):
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

    if output_format == "csv":
        write_csv(results)
    elif output_format == "json":
        write_json(results)
    else:
        log(f"Unknown output format: '{output_format}'!")


def run(output, days):
    results = scrape(days=days)
    validate(results)
    report(results, output_format=output)
