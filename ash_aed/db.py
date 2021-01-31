import psycopg2
from psycopg2.extras import DictCursor

from ash_aed.config import Config
from ash_aed.errors import DatabaseError


class DB:
    """PostgreSQLデータベースへの接続をラップしたクラス。

    Attributes:
        conn (:obj:`psycopg2.connection`): PostgreSQL接続クラス。

    """

    def __init__(self):
        try:
            self.__conn = psycopg2.connect(Config.DATABASE_URL)
        except (psycopg2.DatabaseError, psycopg2.OperationalError) as e:
            raise DatabaseError(e.args[0])

    def cursor(self) -> DictCursor:
        """
        cursorオブジェクトを返す。

        Returns:
            cursor (:obj:`DictCursor`): cursorオブジェクト

        """
        return self.__conn.cursor(cursor_factory=DictCursor)

    def commit(self) -> None:
        """PostgreSQLデータベースにクエリをコミット"""
        return self.__conn.commit()

    def rollback(self) -> None:
        """PostgreSQLデータベースのクエリをロールバック"""
        return self.__conn.rollback()

    def close(self) -> None:
        """PostgreSQLデータベースへの接続を閉じる"""
        return self.__conn.close()
