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
    user_ebay_data,
    gpt4_img_to_title,
)
import json
import logging
from google.cloud import datastore
import os
import secrets
import csv
import jinja2
from ebaysdk.trading import Connection as Trading
import base64
import openai
from openai import OpenAI


secret_key = secrets.token_hex(16)

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


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
            return redirect(url_for("/"))
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
    user_id = user_ebay_data(user_token=session.get("user_token"))

    # 1ページあたりのアイテム数
    page_limit = 30

    # クエリパラメータからカーソルを取得
    start_cursor = request.args.get("cursor", None)
    if start_cursor:
        start_cursor = base64.urlsafe_b64decode(start_cursor.encode("utf-8"))

    # Datastoreのクエリを準備
    query = client.query(kind=f"EbayItem_{user_id}")
    query_iter = query.fetch(limit=page_limit, start_cursor=start_cursor)

    # エンティティを取得
    ebay_items = list(query_iter)

    # 次のページのカーソルを取得
    next_cursor = query_iter.next_page_token
    if next_cursor:
        next_cursor = base64.urlsafe_b64encode(next_cursor).decode("utf-8")

    # テンプレートにデータを渡す
    return render_template(
        "active_listings.html", listings=ebay_items, next_cursor=next_cursor
    )


@app.route("/ebay-connect", methods=["GET", "POST"])
def ebay_connect():
    if request.method == "POST":
        # eBayデータ更新処理を実行
        update_ebay_data()
        return jsonify({"status": "success", "message": "Data updated successfully"})

    return render_template("ebay-connect.html")


def update_ebay_data():
    user_token = session.get("user_token")
    if not user_token:
        print("ユーザートークンが存在しません。")
        return
    # eBay APIの設定
    api = Trading(
        domain="api.ebay.com",
        config_file=None,
        appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",
        devid="8480f8f3-218c-48ff-bd22-0a6787809783",
        certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",
        token=user_token,
        siteid="0",
    )

    entries_per_page = 200  # eBayの最大取得件数に応じて設定
    page_number = 1
    has_more_pages = True

    while has_more_pages:
        request = {
            "DetailLevel": "ReturnAll",
            "Pagination": {
                "EntriesPerPage": entries_per_page,
                "PageNumber": page_number,
            },
            "EndTimeFrom": "2023-11-01T00:00:00",
            "EndTimeTo": "2023-12-31T23:59:59",
        }

        # APIコールを実行して応答を取得
        response = api.execute("GetSellerList", request)
        response_dict = response.dict()

        response_user = api.execute("GetUser", {})
        user_data = response_user.dict()

        # Google Cloud Datastoreクライアントの初期化
        client = datastore.Client()

        # 取得したデータをDatastoreに保存
        for item in response_dict.get("ItemArray", {}).get("Item", []):
            item_id = item.get("ItemID")
            user_id = user_data["User"]["UserID"]

            if not item_id or not user_id:
                continue

            item_data = {
                "Title": item.get("Title"),
                "Price": item.get("SellingStatus", {})
                .get("CurrentPrice", {})
                .get("value"),
                "PictureURL": item.get("PictureDetails", {}).get("PictureURL"),
            }

            # コレクション名（エンティティのキー）をセラー名に基づいて設定
            key = client.key(f"EbayItem_{user_id}", item_id)
            entity = datastore.Entity(key=key)
            entity.update(item_data)
            client.put(entity)

        print("データをDatastoreに保存しました。")

        # 次のページがあるかどうかを確認
        pagination_result = response_dict.get("PaginationResult", {})
        print(pagination_result)
        total_pages = int(pagination_result.get("TotalNumberOfPages", 0))
        print(total_pages)
        has_more_pages = page_number < total_pages
        page_number += 1


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


@app.route("/generate-gpt-title", methods=["POST"])
def generate_gpt_title_endpoint():
    data = request.get_json()
    gpt_description = data.get("gpt_description")
    if not gpt_description:
        return jsonify(status="error", message="Item description is missing."), 400

    try:
        generated_title = gpt4_img_to_title(gpt_description)
    except Exception as e:
        return jsonify(status="error", message=str(e)), 500

    if generated_title:
        return jsonify(status="success", generated_title=generated_title)
    else:
        return jsonify(status="error", message="Failed to generate title."), 400


@app.route("/login")
def login():
    return render_template("login.html")


@app.route("/charts")
def charts():
    return render_template("charts.html")


@app.route("/tables")
def tables():
    return render_template("tables.html")


if __name__ == "__main__":
    app.run(debug=True)
