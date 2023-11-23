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
)
from ebay_api import revise_item_price  # ebay_api.pyから関数をインポート
import logging

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.secret_key = "secret%&LFSJFOS+"


@app.route("/", methods=["GET"])
def index():
    if "user_token" in session:
        return render_template("index.html")
    else:
        return render_template("index.html")


@app.route("/active-listings", methods=["GET"])
def active_listings():
    if "user_token" not in session:
        flash("You must be authenticated to view active listings.", "info")
        return redirect(url_for("index"))  # ホームページへリダイレクト

    user_token = session["user_token"]
    filter_options = {}

    if request.method == "POST":
        # POSTリクエストでフィルターオプションを取得
        filter_options["min_price"] = request.form.get("min_price")
        filter_options["max_price"] = request.form.get("max_price")
        filter_options["category"] = request.form.get("category")
        filter_options["start_time_from"] = request.form.get("start_time_from")
        filter_options["start_time_to"] = request.form.get("start_time_to")
        filter_options["end_time_from"] = request.form.get("end_time_from")
        filter_options["end_time_to"] = request.form.get("end_time_to")

    # フィルターオプションに基づいてセラーリストを取得
    seller_list = get_seller_list(user_token, filter_options)
    active_listings = extract_active_listings(seller_list)

    return render_template("active_listings.html", listings=active_listings)

    # try:
    #     user_token = session["user_token"]
    #     seller_list = get_seller_list(user_token)
    #     active_listings = extract_active_listings(seller_list)
    #     return render_template("active_listings.html", listings=active_listings)
    # except Exception as e:
    #     flash(f"An error occurred: {e}", "danger")
    #     return redirect(url_for("index"))


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
    if "user_token" in session:
        user_token = session["user_token"]
        item_id = request.form["item_id"]  # フォームからアイテムIDを取得
        new_price = request.form["new_price"]  # フォームから新しい価格を取得

        # ebay_api.pyの関数を使って価格を更新
        result = revise_item_price(user_token, item_id, new_price)

        if "Ack" in result and result["Ack"] == "Success":
            flash("Price updated successfully!", "success")
        else:
            flash("Failed to update price.", "danger")

        return redirect(url_for("index"))  # 更新後はホームページにリダイレクト
    else:
        flash("You are not authenticated.", "danger")
        return redirect(url_for("login"))  # 認証されていない場合はログインページにリダイレクト


# @app.route("/update-price", methods=["POST"])
# def update_price():
#     item_id = request.form.get("item_id")
#     new_price = request.form.get("new_price")

#     # 価格のバリデーション（サーバーサイド）
#     if not is_valid_price(new_price):
#         return jsonify({"status": "error", "message": "Invalid price format"}), 400

#     # 価格を更新する処理（省略）

#     return jsonify({"status": "success", "message": "Price updated successfully"})


# # 価格が有効かどうかを確認する関数
# def is_valid_price(price):
#     try:
#         price_val = float(price)
#         return price_val >= 0 and "." in price and len(price.split(".")[1]) <= 2
#     except ValueError:
#         return False


if __name__ == "__main__":
    app.run(debug=True)
