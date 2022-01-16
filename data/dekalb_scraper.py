import requests
import json
from bs4 import BeautifulSoup


def get_available_criteria(session, headers):
    url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
    response = session.get(url, headers=headers)
    soup = BeautifulSoup(response.content, "html.parser")

    return {
        "judicial_officers": [
            {"value": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSJudicialOfficer option")
        ],
        "courtrooms": [
            {"value": el.get("value"), "name": el.get_text()}
            for el in soup.select("#selHSCourtroom option")
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
        "SearchCriteria.SelectedJudicialOfficer": "284",
        "SearchCriteria.DateFrom": "01/31/2022",
        "SearchCriteria.DateTo": "02/24/2022",
    }
    search_result = session.post(
        "https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch",
        data=payload,
        headers=headers,
    )


def read_search_result(session, headers):
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


def extract_fields_of_interest(case):
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

    for criterium in criteria["judicial_officers"]:
        judicial_officer = criterium["name"]
        submit_search_by_judicial_officer(
            session, headers, criterium["value"], "01/31/2022", "02/24/2022"
        )

        result = read_search_result(session, headers)
        result = [extract_fields_of_interest(case) for case in result["Data"]]
        results.extend(result)

    print(json.dumps(results))


run()
