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
from ebay_api import (
    get_seller_list,
    extract_active_listings,
    get_user_token,
    build_auth_url,
    get_item_specifics,
    get_item_description,
)
from ebay_api import revise_item_price  # ebay_api.pyから関数をインポート
import json
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from google.cloud import datastore

logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
app.secret_key = "secret%&LFSJFOS+"


@app.route("/", methods=["GET"])
def index():
    if "user_token" in session:
        return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/active-listings", methods=["GET", "POST"])
def active_listings():
    user_token = session.get("user_token")

    if request.method == "POST":
        try:
            # フォームから価格フィルターを取得
            min_price = request.form.get("min_price", type=float)
            max_price = request.form.get("max_price", type=float)

            # eBay APIから販売リストを取得
            seller_list = get_seller_list(user_token)
            active_listings = extract_active_listings(seller_list)

            # フィルタリング関数を適用
            filtered_listings = filter_listings_by_price(
                active_listings, min_price, max_price
            )
            logging.debug("Filtered listings: %s", filtered_listings)
            # フィルタリングされたリストをJSONで返す
            return jsonify({"listings": filtered_listings})
        except ValueError as e:
            # 価格フィルターの形式が無効な場合、JSONエラーメッセージを返す
            return (
                jsonify(
                    {"error": "Invalid price format. Please enter a valid number."}
                ),
                400,
            )
    else:
        # GETリクエストの場合、全リストを取得
        seller_list = get_seller_list(user_token)
        active_listings = extract_active_listings(seller_list)
        active_listings_with_details = extract_active_listings_with_details(
            seller_list, user_token
        )
        return render_template(
            "active_listings.html", listings=active_listings_with_details
        )


# eBay APIからアクティブなリストを取得して、商品詳細情報を含める
def extract_active_listings_with_details(seller_list, user_token):
    active_items = extract_active_listings(seller_list)
    for item in active_items:
        item_id = item["Item ID"]
        specifics = get_item_specifics(item_id, user_token)
        description = get_item_description(item_id, user_token)
        item["ItemSpecifics"] = specifics  # 商品詳細情報を追加
        item["Description"] = description
    return active_items


def filter_listings_by_price(active_listings, min_price=None, max_price=None):
    filtered_listings = []

    for listing in active_listings:
        # listingが辞書型であるかを確認
        if not isinstance(listing, dict):
            print("Error: Listing is not a dictionary.")
            continue

        price = float(
            listing.get("SellingStatus", {}).get("CurrentPrice", {}).get("Value", 0)
        )

        # 価格に基づいてフィルタリング
        if min_price is not None and price < min_price:
            continue
        if max_price is not None and price > max_price:
            continue

        filtered_listings.append(listing)

    return filtered_listings


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


@app.errorhandler(404)
def page_not_found(e):
    flash("Page not found.", "warning")
    return render_template("404.html"), 404


@app.route("/revise-price", methods=["POST"])
def revise_price():
    if "user_token" not in session:
        flash("You are not authenticated.", "danger")
        return redirect(url_for("login"))

    user_token = session["user_token"]
    item_id = request.form.get("item_id")
    new_price = request.form.get("new_price")

    # 新価格のバリデーション
    try:
        new_price = float(new_price)
        if new_price <= 0:
            raise ValueError("Invalid price")
    except ValueError:
        return jsonify({"status": "error", "message": "Invalid price format"}), 400

    result = revise_item_price(user_token, item_id, new_price)

    if result and result.get("Ack") == "Success":
        return jsonify({"status": "success", "itemId": item_id, "newPrice": new_price})
    else:
        return jsonify({"status": "error", "message": "Failed to update price"}), 400


@app.route("/bulk-update-price", methods=["POST"])
def bulk_update_price():
    user_token = session.get("user_token")
    if not user_token:
        return jsonify({"message": "Authentication required"}), 401

    item_ids = request.form.getlist("item_ids")
    new_price = request.form.get("new_price", type=float)

    updated_items = []
    errors = []

    for item_id in item_ids:
        try:
            # ここでeBay APIを使用して商品の価格を更新
            revise_item_price(user_token, item_id, new_price)
            updated_items.append(item_id)
        except Exception as e:
            errors.append({"item_id": item_id, "error": str(e)})

    return jsonify(
        {
            "message": "Price update process completed.",
            "updated_items": updated_items,
            "errors": errors,
        }
    )


# Google Cloud Datastoreクライアントの初期化
client = datastore.Client()

# 一括更新される商品IDを保存するキー
SELECTED_ITEMS_KEY = "selected_items"

# BackgroundSchedulerの初期化
scheduler = BackgroundScheduler()


def get_selected_items():
    """Datastoreから選択された商品IDを取得する"""
    key = client.key(SELECTED_ITEMS_KEY)
    entity = client.get(key)
    if not entity:
        return []
    return entity["item_ids"]


def save_selected_items(item_ids):
    """Datastoreに選択された商品IDを保存する"""
    key = client.key(SELECTED_ITEMS_KEY)
    entity = datastore.Entity(key=key)
    entity["item_ids"] = item_ids
    client.put(entity)


@app.route("/select-items", methods=["POST"])
def select_items():
    item_ids = request.form.getlist("item_ids")
    save_selected_items(item_ids)
    return jsonify({"status": "success", "selected_items": item_ids})


def daily_price_reduction():
    """毎日特定の時間に選択された商品の価格を1ドル下げる"""
    selected_item_ids = get_selected_items()
    user_token = get_user_token()  # トークンを更新または取得

    for item_id in selected_item_ids:
        try:
            # eBay APIから販売リストを取得
            seller_list = get_seller_list(user_token)
            active_listings = extract_active_listings(seller_list)
            current_price = (
                active_listings.get("SellingStatus", {})
                .get("CurrentPrice", {})
                .get("Value", 0)
            )
            new_price = current_price - 1
            revise_item_price(user_token, item_id, new_price)
        except Exception as e:
            print(f"Error updating price for item {item_id}: {e}")


# スケジューラーの設定と開始
scheduler.add_job(daily_price_reduction, "cron", hour=0)  # 毎日午前0時に実行
scheduler.start()


if __name__ == "__main__":
    app.run(debug=True)
