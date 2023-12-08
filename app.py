from flask import (
    Flask,
    render_template,
    request,
    flash,
    redirect,
    url_for,
    session,
    jsonify,
)
import requests
from ebay_api import (
    get_seller_list,
    extract_active_listings,
    get_user_token,
    build_auth_url,
    revise_item_price,
    get_item_info,
    get_item_price,
    revise_item_title,
)
import json
import logging
from google.cloud import datastore
import os
import secrets
import csv
import jinja2


secret_key = secrets.token_hex(16)

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__, template_folder="templates")
app.secret_key = secrets.token_hex(16)


@app.route("/")
def index():
    client = datastore.Client()
    # DatastoreからEbayItemエンティティを取得
    query = client.query(kind="EbayItem")
    ebay_items = list(query.fetch())
    # index.htmlにデータを渡す
    return render_template("index.html", listings=ebay_items)


@app.route("/ebay/auth")
def ebay_auth():
    # eBayの認証ページにリダイレクト
    flash("Redirecting to eBay for authentication.", "info")
    return redirect(build_auth_url())


@app.route("/ebay/callback")
def ebay_callback():
    auth_code = request.args.get("code")  # eBayからの認証コードを取得
    try:
        logging.info(f"Received auth code: {auth_code}")
        user_token = get_user_token(auth_code)  # 認証コードを使ってトークンを取得
        if user_token:
            logging.info("User token obtained successfully.")
            session["user_token"] = user_token  # トークンをセッションに保存
            # 追加の処理（例えばユーザーをアクティブリストページにリダイレクトするなど）
            return redirect(url_for("active_listings"))
        else:
            logging.warning("Failed to obtain user token.")
            # トークンが取得できなかった場合の処理
            flash("Failed to get user token from eBay.")
            return redirect(url_for("index"))
    except Exception as e:
        logging.error(f"Error during eBay authentication: {e}")
        # エラー処理
        flash(f"Error during eBay authentication: {e}")
        return redirect(url_for("index"))


@app.route("/active-listings", methods=["GET", "POST"])
def active_listings():
    client = datastore.Client()

    # DatastoreからEbayItemエンティティを取得
    query = client.query(kind="EbayItem")
    ebay_items = list(query.fetch())

    # テンプレートにデータを渡す
    return render_template("active_listings.html", listings=ebay_items)


@app.route("/ebay-connect", methods=["GET"])
def ebay_connect():
    if "user_token" in session:
        return render_template("ebay-connect.html")
    else:
        return render_template("ebay-connect.html")


def read_category_ids_from_csv(file_path):
    """
    CSVファイルからカテゴリーIDを読み込む関数。
    """
    category_ids = []
    with open(file_path, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            category_ids.append(row["CategoryId"])
    return category_ids


def fetch_data_from_datastore(client, category_id):
    """
    Datastoreから特定のカテゴリIDに基づくデータを取得する関数。
    """
    query = client.query(kind=f"Watch_{category_id}")
    return list(query.fetch())


@app.route("/layout-static")
def layout_static():
    client = datastore.Client()  # Google Cloud Datastoreクライアントの初期化
    category_ids = read_category_ids_from_csv("categories.csv")

    page = request.args.get("page", 1, type=int)
    per_page = 10  # 1ページあたりのアイテム数

    items = []
    for category_id in category_ids:
        items.extend(fetch_data_from_datastore(client, category_id))

    total_items = len(items)
    total_pages = total_items // per_page + (1 if total_items % per_page else 0)
    start = (page - 1) * per_page
    end = start + per_page

    paginated_items = items[start:end]

    return render_template(
        "layout-static.html", items=paginated_items, page=page, total_pages=total_pages
    )


def fetch_data_terapeak_from_datastore(client):
    """
    Datastoreから全てのデータを取得する関数。
    """
    query = client.query(kind="ItemStats")
    return list(query.fetch())


# カスタムフィルターの定義
def number_format(value, format="%0.2f"):
    return format % value


# カスタムフィルターの追加
app.jinja_env.filters["number_format"] = number_format


@app.route("/layout-sidenav-light")
def layout_sidenav_light():
    client = datastore.Client()
    items = fetch_data_terapeak_from_datastore(client)
    return render_template("layout-sidenav-light.html", items=items)


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/password")
def password():
    return render_template("password.html")


@app.route("/401")
def error_401():
    return render_template("401.html")


@app.route("/404")
def error_404():
    return render_template("404.html")


@app.route("/500")
def error_500():
    return render_template("500.html")


@app.route("/charts")
def charts():
    return render_template("charts.html")


@app.route("/tables")
def tables():
    return render_template("tables.html")


if __name__ == "__main__":
    app.run(debug=True)
