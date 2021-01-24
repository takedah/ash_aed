import unittest

from ash_aed.db import DB
from ash_aed.models import (
    AEDInstallationLocation,
    AEDInstallationLocationFactory,
    CurrentLocation,
)
from ash_aed.services import AEDInstallationLocationService

test_data = [
    {
        "area": "一条通〜十条通",
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
        "area": "一条通〜十条通",
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
    {
        "area": "一条通〜十条通",
        "location_id": 34,
        "location_name": "旭川市ときわ市民ホール",
        "postal_code": "078-8215",
        "address": "北海道旭川市5条通4丁目",
        "phone_number": "0166-23-5577",
        "available_time": "施設休館日を除く， 午前9時〜午後10時",
        "installation_floor": "1階事務室",
        "latitude": 43.77216158,
        "longitude": 142.356329,
    },
    {
        "area": "末広",
        "location_id": 187,
        "location_name": "春光小学校",
        "postal_code": "071-8131",
        "address": "北海道旭川市末広1条1丁目",
        "phone_number": "0166-51-5288",
        "available_time": "",
        "installation_floor": "1階(体育教官室前)廊下",
        "latitude": 43.80256755,
        "longitude": 142.3819691,
    },
    {
        "area": "末広",
        "location_id": 195,
        "location_name": "六合中学校",
        "postal_code": "071-8133",
        "address": "北海道旭川市末広3条2丁目",
        "phone_number": "0166-51-5388",
        "available_time": "",
        "installation_floor": "2階職員室",
        "latitude": 43.80730293,
        "longitude": 142.3777754,
    },
    {
        "area": "花咲",
        "location_id": 357,
        "location_name": "花咲スポーツ公園　球技場",
        "postal_code": "070-0901",
        "address": "北海道旭川市花咲町3丁目",
        "phone_number": "0166-51-5288",
        "available_time": "4月20日〜10月20日(延長の可能性あり)専用使用時のみ",
        "installation_floor": "1階事務室内",
        "latitude": 43.78868943,
        "longitude": 142.3701686,
    },
]


class TestAEDInstallationLocationService(unittest.TestCase):
    @classmethod
    def setUpClass(self):
        self.factory = AEDInstallationLocationFactory()
        for row in test_data:
            self.factory.create(**row)
        self.db = DB()
        self.service = AEDInstallationLocationService(self.db)
        self.current_location = CurrentLocation(
            latitude=43.77082378, longitude=142.3650193
        )

    @classmethod
    def tearDownClass(self):
        self.db.close()

    def test_create(self):
        self.service.truncate()
        for item in self.factory.items:
            self.assertTrue(self.service.create(item))
        self.db.commit()

    def test_get_all(self):
        for item in self.service.get_all():
            self.assertTrue(isinstance(item, AEDInstallationLocation))

    def test_find_by_location_id(self):
        location = self.service.find_by_location_id(9)
        self.assertEqual(location[0].location_name, "フィール旭川")

    def test_find_by_location_name(self):
        results = self.service.find_by_location_name("花咲")
        self.assertEqual(results[0].location_name, "花咲スポーツ公園　球技場")

    def test_get_area_names(self):
        expect = ["一条通〜十条通", "花咲", "末広"]
        self.assertEqual(self.service.get_area_names(), expect)

    def test_find_by_area_name(self):
        area_locations = self.service.find_by_area_name("一条通〜十条通")
        self.assertEqual(area_locations[0].location_name, "旭川市教育委員会")

    def test_get_near_locations(self):
        near_locations = self.service.get_near_locations(self.current_location)
        # 一番近い避難場所
        self.assertEqual(near_locations[0]["order"], 1)
        self.assertEqual(near_locations[0]["location"].location_name, "旭川市教育委員会")
        self.assertEqual(near_locations[0]["distance"], 0.16)
        # 二番目に近い避難場所
        self.assertEqual(near_locations[1]["order"], 2)
        self.assertEqual(near_locations[1]["location"].location_name, "フィール旭川")
        self.assertEqual(near_locations[1]["distance"], 0.71)
        # 五番目に近い避難場所
        self.assertEqual(near_locations[-1]["order"], 5)
        self.assertEqual(near_locations[-1]["location"].location_name, "春光小学校")
        self.assertEqual(near_locations[-1]["distance"], 3.79)


if __name__ == "__main__":
    unittest.main()
