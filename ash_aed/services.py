from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal

from psycopg2.extras import DictCursor

from typing import Optional

from ash_aed.db import DB
from ash_aed.errors import DatabaseError, DataError
from ash_aed.logs import AppLog
from ash_aed.models import (
    AEDInstallationLocation,
    AEDInstallationLocationFactory,
    CurrentLocation,
)


class AEDInstallationLocationService:
    """
    AED設置場所をデータベースに登録し、検索するメソッドを提供する。

    """

    def __init__(self, db: DB):
        """
        Args:
            db (obj:`DB`): psycopg2のメソッドをラップしたメソッドを持つオブジェクト

        """
        self.__db = db
        self.__table_name = "aed_installation_locations"
        self.__logger = AppLog()

    def _execute(self, sql: str, parameters: tuple = None) -> bool:
        """DBオブジェクトのexecuteメソッドのラッパー。

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        """
        return self.__db.execute(sql, parameters)

    def _fetchall(self) -> list:
        """検索結果からAED設置場所データのリストを作成する。

        Returns:
            locations (list of obj:`AEDInstallationLocation`): 検索結果のAED設置場所
                オブジェクトのリスト

        """
        results = self.__db.fetchall()
        factory = AEDInstallationLocationFactory()
        for row in results:
            factory.create(**row)
        return factory.items

    def _fetchone(self) -> DictCursor:
        """DBオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (:obj:`psycopg2.extras.DictCursor`): 検索結果

        """
        return self.__db.fetchone()

    def _info_log(self, message) -> None:
        """AppLogオブジェクトのinfoメソッドのラッパー。

        Args:
            message (str): 通常のログメッセージ
        """
        return self.__logger.info(message)

    def _error_log(self, message) -> None:
        """AppLogオブジェクトのerrorメソッドのラッパー。

        Args:
            message (str): エラーログメッセージ

        """
        return self.__logger.error(message)

    def truncate(self) -> None:
        """AED設置場所テーブルのデータを全削除"""
        state = "TRUNCATE TABLE " + self.__table_name + " RESTART IDENTITY;"
        self._execute(state)
        self._info_log(self.__table_name + "テーブルを初期化しました。")

    def create(self, aed_installation_location: AEDInstallationLocation) -> bool:
        """データベースへAED設置場所データを保存

        Args:
            aed_installation_location (obj:`AEDInstallationLocation`): AED設置場所データ
                のオブジェクト

        Returns:
            bool: データの登録が成功したら真を返す

        """
        items = [
            "area",
            "location_id",
            "location_name",
            "postal_code",
            "address",
            "phone_number",
            "available_time",
            "installation_floor",
            "latitude",
            "longitude",
            "updated_at",
        ]

        column_names = ""
        place_holders = ""
        upsert = ""
        for item in items:
            column_names += "," + item
            place_holders += ",%s"
            upsert += "," + item + "=%s"

        state = (
            "INSERT INTO"
            + " "
            + self.__table_name
            + " "
            + "("
            + column_names[1:]
            + ")"
            + " "
            + "VALUES ("
            + place_holders[1:]
            + ")"
            + " "
            "ON CONFLICT(location_id)" + " "
            "DO UPDATE SET" + " " + upsert[1:]
        )

        temp_values = [
            aed_installation_location.area,
            aed_installation_location.location_id,
            aed_installation_location.location_name,
            aed_installation_location.postal_code,
            aed_installation_location.address,
            aed_installation_location.phone_number,
            aed_installation_location.available_time,
            aed_installation_location.installation_floor,
            aed_installation_location.latitude,
            aed_installation_location.longitude,
            datetime.now(timezone(timedelta(hours=+9))),
        ]
        # UPDATE句用に登録データ配列を重複させる
        values = tuple(temp_values + temp_values)

        try:
            self._execute(state, values)
            return True
        except (DatabaseError, DataError) as e:
            self._error_log(e.message)
            return False

    def get_all(self) -> list:
        """AED設置場所全件データのリストを返す。

        Returns:
            locations (list of obj:`AEDInstallationLocation`): AED設置場所オブジェクト
                全件のリスト

        """
        state = (
            "SELECT area,location_id,location_name,postal_code,address,phone_number,"
            + "available_time,installation_floor,latitude,longitude FROM "
            + self.__table_name
            + " ORDER BY location_id;"
        )
        self._execute(state)
        return self._fetchall()

    def find_by_location_id(self, location_id) -> list:
        """
        AED設置場所連番から該当するAED設置場所データを返す。

        Args:
            location_id (int): AED設置場所連番

        Returns
            aed_installation_location (list of obj:`AEDInstallationLocation`):
                AED設置場所データ

        """
        state = (
            "SELECT area,location_id,location_name,postal_code,address,phone_number,"
            + "available_time,installation_floor,latitude,longitude FROM "
            + self.__table_name
            + " WHERE location_id=%s;"
        )
        self._execute(state, (str(location_id),))
        return self._fetchall()

    def find_by_location_name(self, location_name) -> list:
        """
        指定したAED設置場所名を含むAED設置場所を検索する。

        Args:
            location_name (int): AED設置場所名（キーワード）

        Returns
            aed_installation_location (list of obj:`AEDInstallationLocation`):
                AED設置場所データ

        """
        location_name = "%" + location_name + "%"
        state = (
            "SELECT area,location_id,location_name,postal_code,address,phone_number,"
            + "available_time,installation_floor,latitude,longitude FROM "
            + self.__table_name
            + " WHERE location_name LIKE %s;"
        )
        self._execute(state, (location_name,))
        return self._fetchall()

    def get_area_names(self) -> list:
        """
        AED設置場所の住所の町域一覧を返す。

        Returns:
            area_names (list): AED設置場所の住所の町域のリスト

        """
        state = "SELECT DISTINCT ON (area) area FROM " + self.__table_name + ";"
        area_names = list()
        self._execute(state)
        for row in self.__db.fetchall():
            area_names.append(row["area"])
        return area_names

    def find_by_area_name(self, area_name) -> list:
        """
        町域名からAED設置場所を検索する。

        Args:
            area_name (str): 町域名

        Returns:
            area_locations (list of dicts): 指定した町域名を含む町域のAED設置場所の
                AED設置場所オブジェクトのリスト

        """
        state = (
            "SELECT area,location_id,location_name,postal_code,address,phone_number,"
            + "available_time,installation_floor,latitude,longitude FROM "
            + self.__table_name
            + " WHERE area=%s ORDER BY location_id;"
        )
        self._execute(state, (area_name,))
        return self._fetchall()

    def get_near_locations(self, current_location: CurrentLocation) -> list:
        """
        現在地から直線距離で最も近いAED設置場所上位5件のAED設置場所データのリストを返す。

        Args:
            current_location (obj:`CurrentLocation`): 現在地の緯度経度情報を持つ
                オブジェクト

        Returns:
            near_locations (list of dicts): 現在地から最も近いAED設置場所上位5件の
                AED設置場所オブジェクトと順位、現在地までの距離（キロメートルに換算し
                小数点第3位を切り上げ）を要素に持つ辞書のリスト

        """
        locations = list()
        for location in self.get_all():
            locations.append(
                {
                    "order": None,
                    "location": location,
                    "distance": current_location.get_distance_to(location),
                }
            )
        near_locations = sorted(locations, key=lambda x: x["distance"])[:5]
        for i in range(len(near_locations)):
            # 現在地から近い順で連番を付与する。
            near_locations[i]["order"] = i + 1
            # 距離を分かりやすくするためキロメートルに変換する。
            near_locations[i]["distance"] = float(
                Decimal(str(near_locations[i]["distance"] / 1000)).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            )
        return near_locations

    def get_last_updated(self) -> Optional[datetime]:
        """テーブルの最終更新日を返す。

        Returns:
            last_updated (:obj:`datetime'): テーブルのupdatedカラムで一番最新の
                値を返す。
        """
        self.__db.execute("SELECT max(updated_at) FROM " + self.__table_name + ";")
        row = self._fetchone()
        if row["max"] is None:
            return None
        else:
            return row["max"]
