from datetime import datetime, timedelta, timezone
from decimal import ROUND_HALF_UP, Decimal
from typing import Optional

import psycopg2
from psycopg2.extras import DictCursor

from ash_aed.db import DB
from ash_aed.errors import DatabaseError, DataError, ServiceError
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
            db (obj:`DB`): psycopg2.extrasのDictCursorオブジェクトを返すメソッドを
                ラップしたメソッドを持つオブジェクト

        """
        self.__cursor = db.cursor()
        self.__table_name = "aed_installation_locations"
        self.__logger = AppLog()

    def _execute(self, sql: str, parameters: tuple = None) -> bool:
        """DictCursorオブジェクトのexecuteメソッドのラッパー。

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        """
        try:
            if parameters:
                self.__cursor.execute(sql, parameters)
            else:
                self.__cursor.execute(sql)
            return True
        except (
            psycopg2.DataError,
            psycopg2.IntegrityError,
            psycopg2.InternalError,
        ) as e:
            raise DataError(e.args[0])
        return self.__cursor.execute(sql, parameters)

    def _fetchall(self) -> list:
        """DictCursorオブジェクトのfetchallメソッドのラッパー。

        Returns:
            results (list of :obj:`DictCursor`): 検索結果のリスト

        """
        return self.__cursor.fetchall()

    def _fetchone(self) -> DictCursor:
        """DictCursorオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (:obj:`DictCursor`): 検索結果

        """
        return self.__cursor.fetchone()

    def _get_objects(self) -> list:
        """検索結果からAED設置場所データのリストを作成する。

        Returns:
            locations (list of obj:`AEDInstallationLocation`): 検索結果のAED設置場所
                オブジェクトのリスト

        """
        results = self._fetchall()
        factory = AEDInstallationLocationFactory()
        for row in results:
            factory.create(**row)
        return factory.items

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
        return self._get_objects()

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
        return self._get_objects()

    def find_by_location_name(self, location_name, page: int = 1) -> dict:
        """
        指定したAED設置場所名を含むAED設置場所を検索する。

        Args:
            location_name (int): AED設置場所名（キーワード）
            page (int): 検索結果のページ数

        Returns
            results (dict): 検索結果の総件数と検索条件に合致するAED設置場所データ
                オブジェクトのリスト、ページ分割した際の最大ページ数を要素に持つ辞書

        """
        location_name = "%" + location_name + "%"
        count_state = (
            "SELECT count(location_name) FROM "
            + self.__table_name
            + " WHERE location_name LIKE %s;"
        )
        self._execute(count_state, (location_name,))
        row = self._fetchone()
        results_number = row["count"]

        # 検索結果の最大ページ数を取得。
        max_view_results_number = 10
        if results_number < max_view_results_number:
            max_page = 1
        else:
            if divmod(results_number, max_view_results_number)[1] == 0:
                max_page = divmod(results_number, max_view_results_number)[0]
            else:
                max_page = divmod(results_number, max_view_results_number)[0] + 1

        # 指定されたページ数の検索結果を表示するためにスキップするレコード数を取得。
        try:
            page = int(page)
            if max_page < page:
                raise ServiceError("指定したページ数が上限を超えています。")
            else:
                skip_record_number = (page - 1) * max_view_results_number
        except (TypeError, ValueError):
            raise ServiceError("検索結果のページ指定に誤りがあります。")

        pagenation_option = " LIMIT " + str(max_view_results_number)
        if 1 < page:
            pagenation_option += " OFFSET " + str(skip_record_number)
        pagenation_option += ";"

        # 指定した範囲で検索クエリを実施。
        select_state = (
            "SELECT area,location_id,location_name,postal_code,address,phone_number,"
            + "available_time,installation_floor,latitude,longitude FROM "
            + self.__table_name
            + " WHERE location_name LIKE %s ORDER BY location_id"
        )
        self._execute(select_state + pagenation_option, (location_name,))
        return {
            "all_results_number": results_number,
            "max_page": max_page,
            "pagenated_results_body": self._get_objects(),
        }

    def get_area_names(self) -> list:
        """
        AED設置場所の住所の町域一覧を返す。

        Returns:
            area_names (list): AED設置場所の住所の町域のリスト

        """
        state = "SELECT DISTINCT ON (area) area FROM " + self.__table_name + ";"
        area_names = list()
        self._execute(state)
        for row in self._fetchall():
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
        return self._get_objects()

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
        self._execute("SELECT max(updated_at) FROM " + self.__table_name + ";")
        row = self._fetchone()
        if row["max"] is None:
            return None
        else:
            return row["max"]
