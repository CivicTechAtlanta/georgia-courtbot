import datetime
from unittest import TestCase, mock
import os
import json
from requests import Session
import data.dekalb_scraper


def testdata(named):
    file_path = os.path.join(os.path.dirname(__file__), "testdata", named)
    with open(file_path, "r") as f:
        return f.read()


class TestDateTimeConversion(TestCase):
    def test_hearing_date_to_datetime(self):
        got = data.dekalb_scraper.datetime_to_hearing_date(datetime.date(2007, 12, 5))
        self.assertEqual(got, "12/05/2007")

    def test_datetime_to_hearing_date(self):
        got = data.dekalb_scraper.hearing_date_to_datetime("12/15/2007")
        expected = datetime.datetime(2007, 12, 15)
        self.assertEqual(got, expected)


class TestScraperMethods(TestCase):
    def test_get_all_judicial_officers(self):
        scraper = data.dekalb_scraper.Scraper()
        got = scraper.get_all_judicial_officers(
            testdata("get_all_judicial_officers.raw.html")
        )
        expected = json.loads(testdata("get_all_judicial_officers.scraped.json"))
        self.assertCountEqual(got, expected)

    def test_get_search_result(self):
        scraper = data.dekalb_scraper.Scraper()
        got, has_more_data = scraper.get_search_result(
            testdata("get_search_result-page1.raw.json")
        )
        expected = json.loads(testdata("get_search_result-page1.scraped.json"))
        self.assertTrue(has_more_data)
        self.assertCountEqual(got, expected)

        got, has_more_data = scraper.get_search_result(
            testdata("get_search_result-page2.raw.json")
        )
        expected = json.loads(testdata("get_search_result-page2.scraped.json"))
        self.assertFalse(has_more_data)
        self.assertCountEqual(got, expected)


class TestFetcherMethods(TestCase):
    @mock.patch.object(Session, "get")
    def test_get_all_judicial_officers(self, mock_get):
        cacher = data.dekalb_scraper.Cacher(cache_path=None)
        fetcher = data.dekalb_scraper.Fetcher(cacher=cacher)
        fetcher.get_all_judicial_officers()
        mock_get.assert_called_with(
            "https://ody.dekalbcountyga.gov/portal/Home/Dashboard/26",
            headers={"User-Agent": "CodeForAtlanta Court Bot"},
            verify=False,
        )

    @mock.patch.object(Session, "post")
    def test_search_by_judicial_officer(self, mock_post):
        cacher = data.dekalb_scraper.Cacher(cache_path=None)
        fetcher = data.dekalb_scraper.Fetcher(cacher=cacher)
        fetcher.search_by_judicial_officer(
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
        fetcher.close_session()

    @mock.patch.object(Session, "post")
    def test_get_search_result(self, mock_post):
        cacher = data.dekalb_scraper.Cacher(cache_path=None)
        fetcher = data.dekalb_scraper.Fetcher(cacher=cacher)
        fetcher.get_search_result()
        mock_post.assert_called_with(
            "https://ody.dekalbcountyga.gov/portal/Hearing/HearingResults/Read",
            data={"sort": "", "group": "", "filter": "", "portletId": "27"},
            headers={"User-Agent": "CodeForAtlanta Court Bot"},
        )
        fetcher.close_session()
