import datetime
import requests
import json
import sys
from bs4 import BeautifulSoup


class API:
    def __init__(self):
        self.headers = {"User-Agent": "CodeForAtlanta Court Bot"}
        self.session = requests.Session()

    def get_available_criteria(self):
        url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
        response = self.session.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")

        return {
            "judicial_officers": [
                {"id": el.get("value"), "name": el.get_text()}
                for el in soup.select("#selHSJudicialOfficer option")
            ],
        }

    def submit_search_by_judicial_officer(self, judicial_officer, date_from, date_to):
        payload = {
            "PortletName": "HearingSearch",
            "Settings.CaptchaEnabled": "False",
            "Settings.DefaultLocation": "All Courts",
            "SearchCriteria.SelectedCourt": "All Courts",
            "SearchCriteria.SelectedHearingType": "All Hearings",
            "SearchCriteria.SearchByType": "JudicialOfficer",
            "SearchCriteria.SelectedJudicialOfficer": judicial_officer,
            "SearchCriteria.DateFrom": datetime.date.strftime(date_from, "%m/%d/%Y"),
            "SearchCriteria.DateTo": datetime.date.strftime(date_to, "%m/%d/%Y"),
        }

        self.session.post(
            "https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch",
            data=payload,
            headers=self.headers,
        )

    def get_search_result(self):
        payload = {
            "sort": "",
            "group": "",
            "filter": "",
            "portletId": "27",
        }

        response = self.session.post(
            "https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read",
            data=payload,
            headers=self.headers,
        )

        return json.loads(response.content)

    def fields_of_interest(self, case):
        return {
            "CaseId": case["CaseId"],
            "HearingDate": case["HearingDate"],
            "HearingTime": case["HearingTime"],
            "CourtRoom": case["CourtRoom"],
        }


def log(str):
    print(str, file=sys.stderr)


def run():
    api = API()

    criteria = api.get_available_criteria()

    date_from = datetime.date.today()
    date_to = date_from + datetime.timedelta(days=90)

    results = []

    log("Scraping Dekalb County court cases by judicial officer...")
    log("ID\tName")

    for judicial_officer in criteria["judicial_officers"]:
        log(f'{judicial_officer["id"]}\t{judicial_officer["name"]}')
        api.submit_search_by_judicial_officer(
            judicial_officer["id"], date_from, date_to
        )

        result = api.get_search_result()
        result = [api.fields_of_interest(case) for case in result["Data"]]
        results.extend(result)

    print(json.dumps(results))


run()
