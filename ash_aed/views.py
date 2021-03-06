import os

from flask import Flask, escape, g, render_template, request, url_for

from ash_aed.db import DB
from ash_aed.errors import LocationError, ServiceError
from ash_aed.models import CurrentLocation
from ash_aed.services import AEDInstallationLocationService

app = Flask(__name__)


@app.after_request
def add_security_headers(response):
    response.headers.add(
        "Content-Security-Policy",
        "default-src 'self'; style-src 'self' 'unsafe-inline' \
                    stackpath.bootstrapcdn.com unpkg.com kit.fontawesome.com; \
                    script-src 'self' code.jquery.com cdnjs.cloudflare.com \
                    stackpath.bootstrapcdn.com unpkg.com kit.fontawesome.com; \
                    img-src 'self' *.tile.openstreetmap.org unpkg.com data:; \
                    connect-src ka-f.fontawesome.com; \
                    font-src ka-f.fontawesome.com;",
    )
    response.headers.add("X-Content-Type-Options", "nosniff")
    response.headers.add("X-Frame-Options", "DENY")
    response.headers.add("X-XSS-Protection", "1;mode=block")
    return response


@app.context_processor
def override_url_for():
    return dict(url_for=dated_url_for)


def dated_url_for(endpoint, **values):
    if endpoint == "static":
        filename = values.get("filename", None)
        if filename:
            file_path = os.path.join(app.root_path, endpoint, filename)
            values["q"] = int(os.stat(file_path).st_mtime)
    return url_for(endpoint, **values)


def connect_db():
    return DB()


def get_db():
    if not hasattr(g, "postgres_db"):
        g.postgres_db = connect_db()
    return g.postgres_db


def get_area_names():
    if not hasattr(g, "area_names"):
        service = AEDInstallationLocationService(get_db())
        g.area_names = service.get_area_names()
    return g.area_names


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, "postgres_db"):
        g.postgres_db.close()


@app.route("/")
def index():
    title = "トップページ"
    service = AEDInstallationLocationService(get_db())
    last_updated = service.get_last_updated().strftime("%Y/%m/%d %H:%M")
    return render_template(
        "index.html",
        title=title,
        area_names=get_area_names(),
        last_updated=last_updated,
    )


@app.route("/search_by_gps", methods=["GET", "POST"])
def search_by_gps():
    if request.method == "GET":
        title = "トップページ"
        return render_template("index.html", title=title, area_names=get_area_names())
    else:
        title = "現在地から近いAED設置場所の検索結果"
        current_latitude = escape(request.form["current_latitude"])
        current_longitude = escape(request.form["current_longitude"])
        try:
            current_latitude = float(current_latitude)
            current_longitude = float(current_longitude)
            current_location = CurrentLocation(
                latitude=current_latitude, longitude=current_longitude
            )
        except (LocationError, ValueError):
            title = "検索条件に誤りがあります"
            error_message = "緯度経度が正しくありません。"
            return render_template(
                "error.html",
                title=title,
                area_names=get_area_names(),
                error_message=error_message,
            )

        service = AEDInstallationLocationService(get_db())
        near_locations = service.get_near_locations(current_location)
        results_length = len(near_locations)
        return render_template(
            "search_by_gps.html",
            title=title,
            area_names=get_area_names(),
            search_results=near_locations,
            current_latitude=current_latitude,
            current_longitude=current_longitude,
            results_length=results_length,
        )


@app.route("/location/<location_id>")
def location(location_id):
    location_id = escape(location_id)
    try:
        location_id = int(location_id)
    except ValueError:
        title = "検索条件に誤りがあります"
        error_message = "AED設置場所の連番が正しくありません。"
        return render_template(
            "error.html",
            title=title,
            area_names=get_area_names(),
            error_message=error_message,
        )

    service = AEDInstallationLocationService(get_db())
    result = service.find_by_location_id(location_id)
    if len(result) == 0:
        title = "検索条件に誤りがあります"
        error_message = "そのようなAED設置場所連番はありません。"
        return render_template(
            "error.html",
            title=title,
            area_names=get_area_names(),
            error_message=error_message,
        )

    title = "AED設置場所「" + result[0].location_name + "」の情報"
    return render_template(
        "location.html",
        title=title,
        area_names=get_area_names(),
        result=result[0],
    )


@app.route("/area/<area_name>")
def area(area_name):
    area_name = escape(area_name)
    service = AEDInstallationLocationService(get_db())
    search_results = service.find_by_area_name(area_name)
    results_length = len(search_results)
    if results_length == 0:
        title = "検索条件に誤りがあります"
        error_message = "地域の名称が正しくありません。"
        return render_template(
            "error.html",
            title=title,
            area_names=get_area_names(),
            error_message=error_message,
        )

    title = "「" + area_name + "」のAED設置場所"
    return render_template(
        "area.html",
        title=title,
        area_names=get_area_names(),
        area_name=area_name,
        search_results=search_results,
        results_length=results_length,
    )


@app.route("/find_by_location_name")
def find_by_location_name():
    location_name = escape(request.args.get("location_name", ""))
    page = escape(request.args.get("page", 1))
    try:
        page = int(page)
    except ValueError:
        title = "検索条件に誤りがあります"
        error_message = "ページ数指定が正しくありません。"
        return render_template(
            "error.html",
            title=title,
            area_names=get_area_names(),
            error_message=error_message,
        )

    service = AEDInstallationLocationService(get_db())
    try:
        search_results = service.find_by_location_name(location_name, page)
    except ServiceError as e:
        title = "検索条件に誤りがあります"
        error_message = e.message
        return render_template(
            "error.html",
            title=title,
            area_names=get_area_names(),
            error_message=error_message,
        )

    title = "名称に「" + location_name + "」を含むのAED設置場所の検索結果"
    if 1 < page:
        title += "（" + str(page) + "ページ）"
    return render_template(
        "find_by_location_name.html",
        title=title,
        area_names=get_area_names(),
        location_name=location_name,
        results_body=search_results["pagenated_results_body"],
        results_number=search_results["all_results_number"],
        page=page,
        max_page=search_results["max_page"],
    )


@app.errorhandler(404)
def not_found(error):
    title = "404 Page Not Found."
    return render_template("404.html", title=title, area_names=get_area_names())


if __name__ == "__main__":
    app.run(debug=True)
