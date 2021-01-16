import io
import numpy as np
import pandas as pd
import requests
from ash_aed.config import Config
from ash_aed.errors import ScrapeError
from ash_aed.logs import AppLog
from requests import RequestException


class OpenData:
    """旭川市オープンデータライブラリからCSVをダウンロードしてテキスト要素の二次元配列に格納する

    Attributes:
        lists(list of dicts): CSVの各行を辞書にしてリストに格納したデータ

    """

    def __init__(self):
        self.__lists = list()
        logger = AppLog()
        # 旭川市ホームページのTLS証明書のDH鍵長に問題があるためセキュリティを下げて回避する
        requests.packages.urllib3.util.ssl_.DEFAULT_CIPHERS += "HIGH:!DH"
        try:
            response = requests.get(Config.OPENDATA_URL)
            logger.info("オープンデータのダウンロードに成功しました。")
        except RequestException as e:
            message = e.args[0]
            logger.error(message)
            raise ScrapeError(message)

        csv_content = io.BytesIO(response.content)
        df = pd.read_csv(csv_content, encoding="cp932", header=0, dtype=str)
        df.replace(np.nan, "", inplace=True)
        for row in df.values.tolist():
            self.__lists.append(
                {
                    "area": row[0],
                    "location_id": int(row[1]),
                    "location_name": row[2],
                    "postal_code": row[3],
                    "address": row[4],
                    "phone_number": row[5],
                    "available_time": row[6],
                    "installation_floor": row[7],
                    "latitude": float(row[8]),
                    "longitude": float(row[9]),
                }
            )

    @property
    def lists(self) -> list:
        return self.__lists
