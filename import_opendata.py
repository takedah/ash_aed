from ash_aed.db import DB
from ash_aed.errors import DatabaseError, DataError
from ash_aed.logs import AppLog
from ash_aed.models import AEDInstallationLocationFactory
from ash_aed.scraper import OpenData
from ash_aed.services import AEDInstallationLocationService


def import_opendata():
    """データベースに旭川市オープンデータのAED設置事業所一覧データを格納"""

    open_data = OpenData()
    factory = AEDInstallationLocationFactory()
    for row in open_data.lists:
        factory.create(row)

    db = DB()
    logger = AppLog()
    try:
        service = AEDInstallationLocationService(db)
        service.truncate()
        for aed_installation_location in factory.items:
            service.create(aed_installation_location)
        db.commit()
        logger.info("データベースへAED設置事業所一覧オープンデータをインポートしました。")
    except (DatabaseError, DataError) as e:
        db.rollback()
        logger.error(e.message)
    finally:
        db.close()


if __name__ == "__main__":
    import_opendata()
