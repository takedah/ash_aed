import unittest

from ash_aed.errors import LocationError
from ash_aed.models import (AEDInstallationLocation,
                            AEDInstallationLocationFactory, CurrentLocation,
                            Point)

test_data = {
    "area": "一条通〜十条通",
    "location_id": 9,
    "location_name": "フィール旭川",
    "postal_code": "070-0031",
    "address": "北海道旭川市1条通8丁目",
    "phone_number": "0166-25-5443",
    "available_time": "※平日午前8時45分から午後7時30分まで土日祝午前10時から午後7時",
    "installation_floor": "7階国際交流スペース内",
    "latitude": 43.76572279,
    "longitude": 142.3597048,
}


class TestPoint(unittest.TestCase):
    def setUp(self):
        self.point = Point(latitude=43.7703945, longitude=142.3631408)

    def test_init(self):
        with self.assertRaises(LocationError):
            Point(latitude="hoge", longitude="fuga")
        with self.assertRaises(LocationError):
            Point(latitude=-90, longitude=180)

    def test_latitude(self):
        self.assertEqual(self.point.latitude, 43.7703945)

    def test_longitude(self):
        self.assertEqual(self.point.longitude, 142.3631408)


class TestAEDInstallationLocation(unittest.TestCase):
    def setUp(self):
        self.aed_installation_location = AEDInstallationLocation(**test_data)

    def test_area(self):
        self.assertEqual(self.aed_installation_location.area, "一条通〜十条通")

    def test_location_id(self):
        self.assertEqual(self.aed_installation_location.location_id, 9)

    def test_location_name(self):
        self.assertEqual(self.aed_installation_location.location_name, "フィール旭川")

    def test_postal_code(self):
        self.assertEqual(self.aed_installation_location.postal_code, "070-0031")

    def test_address(self):
        self.assertEqual(self.aed_installation_location.address, "北海道旭川市1条通8丁目")

    def test_phone_number(self):
        self.assertEqual(self.aed_installation_location.phone_number, "0166-25-5443")

    def test_available_time(self):
        self.assertEqual(
            self.aed_installation_location.available_time,
            "※平日午前8時45分から午後7時30分まで土日祝午前10時から午後7時",
        )

    def test_installation_floor(self):
        self.assertEqual(
            self.aed_installation_location.installation_floor, "7階国際交流スペース内"
        )


class TestAEDInstallationLocationFactory(unittest.TestCase):
    def test_create(self):
        factory = AEDInstallationLocationFactory()
        # AEDInstallationLocationクラスのオブジェクトが生成できるか確認する。
        aed_installation_location = factory.create(test_data)
        self.assertTrue(isinstance(aed_installation_location, AEDInstallationLocation))
        for obj in factory.items:
            self.assertTrue(isinstance(obj, AEDInstallationLocation))


class TestCurrentLocation(unittest.TestCase):
    def setUp(self):
        factory = AEDInstallationLocationFactory()
        self.aed_installation_location = factory.create(test_data)
        self.current_location = CurrentLocation(
            latitude=43.7703945, longitude=142.3631408
        )

    def test_get_distance_to(self):
        result = self.current_location.get_distance_to(self.aed_installation_location)
        self.assertEqual(result, 588.855)


if __name__ == "__main__":
    unittest.main()
