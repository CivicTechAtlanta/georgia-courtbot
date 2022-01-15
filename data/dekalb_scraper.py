import requests
import json
from bs4 import BeautifulSoup


headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0"
}

url = "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26"
session = requests.Session()
response = session.get(url, headers=headers)
soup = BeautifulSoup(response.content, "html.parser")

judicial_officers = [
    {"value": el.get("value"), "name": el.get_text()}
    for el in soup.select("#selHSJudicialOfficer option")
]

courtrooms = [
    {"value": el.get("value"), "name": el.get_text()}
    for el in soup.select("#selHSCourtroom option")
]

result = {"judicial_officers": judicial_officers, "courtrooms": courtrooms}

print(json.dumps(result))
