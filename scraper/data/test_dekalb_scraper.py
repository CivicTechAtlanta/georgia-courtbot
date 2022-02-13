from unittest import TestCase, mock
from pathlib import Path
import os
import json
from requests import Session
import data.dekalb_scraper


def read_testdata(named):
    file_path = os.path.join(os.path.dirname(__file__), "testdata", named)
    with open(file_path, "r") as f:
        return f.read()


class TestScraperMethods(TestCase):
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
