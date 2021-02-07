import os


class Config:
    DATABASE_URL = os.environ.get("ASH_AED_DB_URL")
    OPENDATA_URL = (
        "https://www.city.asahikawa.hokkaido.jp/kurashi/311/316/d053328_d/fil/"
        + "012041_aed_location.csv"
    )
