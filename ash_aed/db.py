import psycopg2
from psycopg2.extras import DictCursor

from ash_aed.config import Config
from ash_aed.errors import DatabaseError, DataError


class DB:
    """PostgreSQLデータベースの操作を行う。

    Attributes:
        conn (:obj:`psycopg2.connection`): PostgreSQL接続クラス。

    """

    def __init__(self):
        try:
            self.__conn = psycopg2.connect(Config.DATABASE_URL)
            self.__cursor = self.__conn.cursor(cursor_factory=DictCursor)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            raise DatabaseError(e.args[0])

    def execute(self, sql: str, parameters: tuple = None) -> bool:
        """cursorオブジェクトのexecuteメソッドのラッパー。

        Args:
            sql (str): SQL文
            parameters (tuple): SQLにプレースホルダを使用する場合の値を格納したリスト

        Returns:
            bool: 成功したら真を返す。

        Raises:
            DataError: SQL実行でエラーが生じた場合

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

    def fetchall(self) -> list:
        """cursorオブジェクトのfetchallメソッドのラッパー。

        Returns:
            results (list of obj:`DictCursor`): 連想配列風に検索結果を格納したデータのリスト

        """
        return self.__cursor.fetchall()

    def fetchone(self) -> DictCursor:
        """cursorオブジェクトのfetchoneメソッドのラッパー。

        Returns:
            results (obj:`DictCursor`): 連想配列風に検索結果を格納したデータ

        """
        return self.__cursor.fetchone()

    def commit(self) -> None:
        """PostgreSQLデータベースにクエリをコミット"""
        return self.__conn.commit()

    def rollback(self) -> None:
        """PostgreSQLデータベースのクエリをロールバック"""
        return self.__conn.rollback()

    def close(self) -> None:
        """PostgreSQLデータベースへの接続を閉じる"""
        return self.__conn.close()
