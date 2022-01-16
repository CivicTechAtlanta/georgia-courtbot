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

    log("Scraping Dekalb County court cases per judicial officer...")
    log("ID\tName")

    for judicial_officer in criteria["judicial_officers"]:
        log(f'{judicial_officer["id"]}\t{judicial_officer["name"]}')
        api.submit_search_by_judicial_officer(
            judicial_officer["id"], date_from, date_to
        )

        result = api.get_search_result()
        result = [api.fields_of_interest(case) for case in result["Data"]]
        results.extend(result)
    log("Finished.")

    print(json.dumps(results))


run()
