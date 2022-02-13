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
        mock_resp = mock.Mock()
        mock_resp.status_code = 200
        mock_resp.content = read_testdata("26.html")
        mock_get.return_value = mock_resp
        scraper = data.dekalb_scraper.Scraper()
        scraper.close_session()
        got = [x for x in scraper.get_all_judicial_officers()]
        expected = json.loads(read_testdata("output.json"))
        self.assertCountEqual(got, expected)

    """
    @mock.patch.object(Session, "post")
    def search_by_judicial_officer(self, mock_post):
        gt
        """
