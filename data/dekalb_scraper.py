import datetime
import requests
import json
from bs4 import BeautifulSoup


def get_available_criteria(session, headers):
    url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    return {
        "judicial_officers": [
            {"id": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSJudicialOfficer option")
        ],
    }


def submit_search_by_judicial_officer(
    session, headers, judicial_officer, date_from, date_to
):
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

    session.post(
        "https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch",
        data=payload,
        headers=headers,
    )


def get_search_result(session, headers):
    payload = {
        "sort": "",
        "group": "",
        "filter": "",
        "portletId": "27",
    }

    result = session.post(
        "https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read",
        data=payload,
        headers=headers,
    )

    return json.loads(result.content)


def fields_of_interest(case):
    return {
        "CaseId": case["CaseId"],
        "HearingDate": case["HearingDate"],
        "HearingTime": case["HearingTime"],
        "CourtRoom": case["CourtRoom"],
    }


def run():
    headers = {"User-Agent": "CodeForAtlanta Court Bot"}

    session = requests.Session()

    criteria = get_available_criteria(session, headers)

    results = []

    date_from = datetime.date.today()
    date_to = date_from + datetime.timedelta(days=90)

    for judicial_officer in criteria["judicial_officers"]:
        submit_search_by_judicial_officer(
            session, headers, judicial_officer["id"], date_from, date_to
        )

        result = get_search_result(session, headers)
        result = [fields_of_interest(case) for case in result["Data"]]
        results.extend(result)

    print(json.dumps(results))


run()
