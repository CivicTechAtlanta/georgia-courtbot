import datetime
from unittest import TestCase, mock
import os
import json
from requests import Session
import data.dekalb_scraper


def read_testdata(named):
    file_path = os.path.join(os.path.dirname(__file__), "testdata", named)
    with open(file_path, "r") as f:
        return f.read()


class TestScraperMethods(TestCase):
    def test_hearing_date_to_datetime(self):
        got = data.dekalb_scraper.datetime_to_hearing_date(datetime.date(2007, 12, 5))
        self.assertEqual(got, "12/05/2007")

    def test_datetime_to_hearing_date(self):
        got = data.dekalb_scraper.hearing_date_to_datetime("12/15/2007")
        expected = datetime.datetime(2007, 12, 15)
        self.assertEqual(got, expected)

    @mock.patch.object(Session, "get")
    def test_get_all_judicial_officers(self, mock_get):
        mock_get.return_value = mock.Mock(
            status_code=200, content=read_testdata("26.html")
        )
        scraper = data.dekalb_scraper.Scraper()
        scraper.close_session()
        got = [x for x in scraper.get_all_judicial_officers()]
        expected = json.loads(read_testdata("output.json"))
        self.assertCountEqual(got, expected)

    @mock.patch.object(Session, "post")
    def test_search_by_judicial_officer(self, mock_post):
        scraper = data.dekalb_scraper.Scraper()
        scraper.search_by_judicial_officer(
            "judge_named", datetime.datetime(2021, 1, 1), datetime.datetime(2021, 5, 1)
        )
        mock_post.assert_called_with(
            "https://ody.dekalbcountyga.gov/portal/Hearing/SearchHearings/HearingSearch",
            data={
                "PortletName": "HearingSearch",
                "Settings.CaptchaEnabled": "False",
                "Settings.DefaultLocation": "All Courts",
                "SearchCriteria.SelectedCourt": "All Courts",
                "SearchCriteria.SelectedHearingType": "All Hearings",
                "SearchCriteria.SearchByType": "JudicialOfficer",
                "SearchCriteria.SelectedJudicialOfficer": "judge_named",
                "SearchCriteria.DateFrom": "01/01/2021",
                "SearchCriteria.DateTo": "05/01/2021",
            },
            headers={"User-Agent": "CodeForAtlanta Court Bot"},
        )
        scraper.close_session()

    @mock.patch.object(Session, "post")
    def test_get_search_result(self, mock_post):
        expected = {"returned": "this json object"}
        scraper = data.dekalb_scraper.Scraper()
        mock_post.return_value = mock.Mock(
            status_code=200, content=json.dumps(expected)
        )
        result = scraper.get_search_result()
        self.assertEqual(result, expected)
        mock_post.assert_called_with(
            "https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read",
            data={"sort": "", "group": "", "filter": "", "portletId": "27"},
            headers={"User-Agent": "CodeForAtlanta Court Bot"},
        )
        scraper.close_session()
