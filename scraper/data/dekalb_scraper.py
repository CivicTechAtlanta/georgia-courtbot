import datetime
import requests
import json
import sys
import csv
import jsonschema
import os
from bs4 import BeautifulSoup


class Cacher:
    def __init__(self, cache_path):
        self.cache_path = cache_path

    def write(self, filepath, content):
        if self.cache_path is None:
            return

        path = os.path.join(self.cache_path, filepath)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb+") as f:
            f.write(content)


class Scraper:
    def __init__(self):
        pass

    def get_all_judicial_officers(self, content):
        soup = BeautifulSoup(content, "html.parser")

        result = [
            {"id": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSJudicialOfficer option")
        ]

        return filter(lambda e: e["name"] != "", result)

    def get_search_result(self, content):
        obj = json.loads(content)
        return (obj["Data"], obj["MaxResultsHit"])


class Fetcher:
    def __init__(self, cacher):
        self.headers = {"User-Agent": "CodeForAtlanta Court Bot"}
        self.session = requests.Session()
        self.cacher = cacher

    def close_session(self):
        self.session.close()

    def get_all_judicial_officers(self):
        url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
        response = self.session.get(url, headers=self.headers)
        self.cacher.write("get_all_judicial_officers", response.content)
        return response.content

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

        response = self.session.post(
            url,
            data=data,
            headers=self.headers,
        )

        self.cacher.write("search_by_judicial_officer", response.content)

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

        self.cacher.write(
            f"get_search_result_{datetime.datetime.now()}", response.content
        )

        return response.content


def find_last_case(cases):
    return max(cases, key=lambda case: hearing_date_to_datetime(case["HearingDate"]))


def hearing_date_to_datetime(string):
    return datetime.datetime.strptime(string, "%m/%d/%Y")


def datetime_to_hearing_date(dt):
    return datetime.date.strftime(dt, "%m/%d/%Y")


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


def scrape(days, cache_path):
    cacher = Cacher(cache_path)
    fetcher = Fetcher(cacher)
    scraper = Scraper()

    date_from = datetime.date.today()
    date_to = date_from + datetime.timedelta(days)

    results = []

    log(
        f"Scraping Dekalb County court cases per judicial officer from {date_from} to {date_to}.",
        f"---",
        f"ID\tName\t",
    )

    officers = scraper.get_all_judicial_officers(fetcher.get_all_judicial_officers())

    def fetch(officer_id, date_from, date_to):
        fetcher.search_by_judicial_officer(officer_id, date_from, date_to)
        cases, hasMoreData = scraper.get_search_result(fetcher.get_search_result())
        if hasMoreData == True:
            last_case = find_last_case(cases)
            offset_date = hearing_date_to_datetime(last_case["HearingDate"])
            page = fetch(officer, offset_date, date_to)
            cases.extend(case for case in page if case not in cases)

        return cases

    for officer in officers:
        log(f'{officer["id"]}\t{officer["name"]}')
        results.extend(
            [
                take_fields_of_interest(case)
                for case in fetch(officer["id"], date_from, date_to)
            ]
        )

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


def run(output, days, cache_path):
    results = scrape(days=days, cache_path=cache_path)
    validate(results)
    report(results, output_format=output)
