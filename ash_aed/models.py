import numpy as np
from decimal import Decimal
from decimal import ROUND_HALF_UP
from ash_aed.errors import LocationError
from ash_aed.factory import Factory


class Point:
    """
    緯度と経度を要素に持つ地点情報を表す。

    Attributes:
        latitude (float): 緯度（北緯）を表す小数
        longitude (float): 経度（東経）を表す小数

    """

    def __init__(self, latitude: float, longitude: float):
        """
        Args:
            latitude (float): 緯度（北緯）を表す小数
            longitude (float): 経度（東経）を表す小数

        """
        try:
            latitude = float(latitude)
            longitude = float(longitude)
        except (TypeError, ValueError):
            raise LocationError("緯度経度は数値で指定してください。")
        if -90 < latitude and latitude < 90:
            self.__latitude = latitude
        else:
            raise LocationError("緯度に指定できない値が設定されています。")
        if -180 < longitude and longitude < 180:
            self.__longitude = longitude
        else:
            raise LocationError("経度に指定できない値が設定されています。")

    @property
    def latitude(self) -> float:
        return self.__latitude

    @property
    def longitude(self) -> float:
        return self.__longitude


class AEDInstallationLocation(Point):
    """AED設置場所のデータモデル

    Attributes:
        area (str): AED設置場所がある地区
        location_id (int): 連番
        location_name (str): AED設置場所名
        postal_code (str): AED設置場所の郵便番号
        address (str): AED設置場所の住所
        phone_number (str): AED設置場所の電話番号
        available_time (str): AED設置場所の利用可能な時間
        installation_floor (str): AEDが設置されているフロア
        latitude (float): AED設置場所の緯度
        longitude (float): AED設置場所の経度

    """

    def __init__(self, **kwargs: dict):
        """
        Args:
            **kwargs: AED設置場所の情報を格納したディクショナリ

        """
        self.__area = str(kwargs["area"])
        self.__location_id = int(kwargs["location_id"])
        self.__location_name = str(kwargs["location_name"])
        self.__postal_code = str(kwargs["postal_code"]).strip()
        self.__address = str(kwargs["address"])
        self.__phone_number = str(kwargs["phone_number"])
        self.__available_time = str(kwargs["available_time"])
        self.__installation_floor = str(kwargs["installation_floor"])
        Point.__init__(self, float(kwargs["latitude"]), float(kwargs["longitude"]))

    @property
    def area(self) -> str:
        return self.__area

    @property
    def location_id(self) -> int:
        return self.__location_id

    @property
    def location_name(self) -> str:
        return self.__location_name

    @property
    def postal_code(self) -> str:
        return self.__postal_code

    @property
    def address(self) -> str:
        return self.__address

    @property
    def phone_number(self) -> str:
        return self.__phone_number

    @property
    def available_time(self) -> str:
        return self.__available_time

    @property
    def installation_floor(self) -> str:
        return self.__installation_floor


class AEDInstallationLocationFactory(Factory):
    """AED設置場所モデルを作成する。

    Attributes:
        items (list of :obj:`AEDInstallationLocation`): AED設置場所オブジェクトのリスト

    """

    def __init__(self):
        self.__items = list()

    @property
    def items(self) -> list:
        return self.__items

    def _create_item(self, row: dict) -> AEDInstallationLocation:
        """AED設置場所オブジェクトを作成する。

        Args:
            row (dict): AED設置場所情報を表すディクショナリ

        """
        return AEDInstallationLocation(**row)

    def _register_item(self, item: AEDInstallationLocation) -> bool:
        """AED設置場所オブジェクトをリストに追加。

        Args:
            item (:obj:`AEDInstallationLocation`): AED設置場所オブジェクト

        Returns:
            bool: 成功したら真を返す

        """
        self.__items.append(item)
        return True


class CurrentLocation(Point):
    """
    現在地の情報を表す

    Attributes:
        latitude (float): AED設置場所の緯度
        longitude (float): AED設置場所の経度

    """

    def __init__(self, latitude: float, longitude: float):
        """
        Args:
            latitude (float): 緯度（北緯）を表す小数
            longitude (float): 経度（東経）を表す小数

        """
        Point.__init__(self, latitude, longitude)

    def get_distance_to(self, end_point: Point) -> float:
        """
        現在地とAED設置場所の2点間の距離を計算して返す。

        Args:
            end_point (obj:`Point`): AED設置場所の緯度と経度を持つオブジェクト

        Returns:
            distance (float): 現在地とAED設置場所の2点間の距離（メートル、
                小数点以下第4位を切り上げ）

        """
        earth_radius = 6378137.00
        start_latitude = np.radians(self.latitude)
        start_longitude = np.radians(self.longitude)
        end_latitude = np.radians(end_point.latitude)
        end_longitude = np.radians(end_point.longitude)
        distance = earth_radius * np.arccos(
            np.sin(start_latitude) * np.sin(end_latitude)
            + np.cos(start_latitude)
            * np.cos(end_latitude)
            * np.cos(end_longitude - start_longitude)
        )
        return float(
            Decimal(str(distance)).quantize(Decimal("0.001"), rounding=ROUND_HALF_UP)
        )
