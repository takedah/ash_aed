# 旭川市AED設置場所検索

旭川市ホームページからダウンロードしたAED設置場所一覧CSVから、旭川市のAED設置場所を検索できるようにしたサービスです。

## Description

ToDo

## Requirement

- PostgreSQL
- flask
- gunicorn
- numpy
- pandas
- psycopg2
- requests

## Install

```bash
$ export ASH_AED_DB_URL=postgresql://{user_name}:{password}@{host_name}/{db_name}
$ psql -f db/schema.sql -U {user_name} -d {db_name} -h {host_name}
$ make
```

## Usage

```bash
$ gunicorn run:app
```

## Lisence

Copyright (c) 2021 Hiroki Takeda
[MIT](http://opensource.org/licenses/mit-license.php)
