from flask import Flask, render_template, request, flash, redirect, url_for, session
from ebay_api import (
    get_seller_list,
    extract_active_listings,
    get_user_token,
    build_auth_url,
)
import logging

logging.basicConfig(level=logging.INFO)


app = Flask(__name__)
app.secret_key = "secret%&LFSJFOS+"


@app.route("/", methods=["GET"])
def index():
    if "user_token" in session:
        return redirect(url_for("active_listings"))
    else:
        return render_template("index.html")


@app.route("/active-listings", methods=["GET"])
def active_listings():
    if "user_token" not in session:
        flash("You must be authenticated to view active listings.", "info")
        return redirect(url_for("index"))  # ホームページへリダイレクト

    try:
        user_token = session["user_token"]
        seller_list = get_seller_list(user_token)
        active_listings = extract_active_listings(seller_list)
        return render_template("active_listings.html", listings=active_listings)
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("index"))


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


if __name__ == "__main__":
    app.run(debug=True)
