import unittest
from unittest.mock import Mock, patch

from requests import ConnectionError, HTTPError, Timeout

from ash_aed.errors import ScrapeError
from ash_aed.scraper import OpenData


class TestOpenData(unittest.TestCase):
    @patch("ash_aed.scraper.requests")
    def test_lists(self, mock_requests):
        csv_content = (
            "地区,連番,設置事業所名,郵便番号,住所,電話番号,利用可能時間,ＡＥＤ設置場所,"
            + "地図の緯度,地図の経度"
            + "\r\n"
            + "一条通〜十条通,1,旭川市教育委員会,070-0036,"
            + "北海道旭川市6条通8丁目セントラル旭川ビル6階,0166-25-7534,,6階教育政策課,"
            + "43.7703945,142.3631408"
            + "\r\n"
            + "一条通〜十条通,9,フィール旭川,070-0031,北海道旭川市1条通8丁目,"
            + "0166-25-5443,"
            + "※平日午前8時45分から午後7時30分まで土日祝午前10時から午後7時30分まで,"
            + "7階国際交流スペース内,43.76572279,142.3597048"
        )
        mock_requests.get.return_value = Mock(
            status_code=200, content=csv_content.encode("cp932")
        )
        expect = [
            {
                "area": "一条通～十条通",
                "location_id": 1,
                "location_name": "旭川市教育委員会",
                "postal_code": "070-0036",
                "address": "北海道旭川市6条通8丁目セントラル旭川ビル6階",
                "phone_number": "0166-25-7534",
                "available_time": "",
                "installation_floor": "6階教育政策課",
                "latitude": 43.7703945,
                "longitude": 142.3631408,
            },
            {
                "area": "一条通～十条通",
                "location_id": 9,
                "location_name": "フィール旭川",
                "postal_code": "070-0031",
                "address": "北海道旭川市1条通8丁目",
                "phone_number": "0166-25-5443",
                "available_time": "※平日午前8時45分から午後7時30分まで土日祝午前10時から午後7時30分まで",
                "installation_floor": "7階国際交流スペース内",
                "latitude": 43.76572279,
                "longitude": 142.3597048,
            },
        ]
        open_data = OpenData()
        self.assertEqual(open_data.lists, expect)

        mock_requests.get.side_effect = Timeout("Dummy Error.")
        with self.assertRaises(ScrapeError):
            OpenData()

        mock_requests.get.side_effect = HTTPError("Dummy Error.")
        with self.assertRaises(ScrapeError):
            OpenData()

        mock_requests.get.side_effect = ConnectionError("Dummy Error.")
        with self.assertRaises(ScrapeError):
            OpenData()


if __name__ == "__main__":
    unittest.main()
