from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import requests
import json
import logging
import os
import secrets
import csv
import base64
import traceback
import tempfile
import uuid
from google.cloud import datastore, storage
from ebaysdk.trading import Connection as Trading
from ebay_api import (
    get_seller_list, get_user_token, build_auth_url,user_ebay_data,get_financial_data
)
from models import Transaction  # データベースモデルをインポート


# ロギングの設定
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, template_folder="templates")
CORS(app)

# データベース設定
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sales_management.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# セッションの設定
app.secret_key = secrets.token_hex(16)

# モデル定義
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    platform = db.Column(db.String(50), nullable=False)
    product_name = db.Column(db.String(200), nullable=False)
    sale_amount = db.Column(db.Float, nullable=False)
    purchase_cost = db.Column(db.Float, nullable=False)
    shipping_cost = db.Column(db.Float, nullable=False)
    profit = db.Column(db.Float, nullable=False)

# ルート定義
@app.route("/")
def index():
    client = datastore.Client()
    query = client.query(kind="EbayItem")
    ebay_items = list(query.fetch())
    return render_template("index.html", listings=ebay_items)

@app.route("/ebay/auth")
def ebay_auth():
    flash("Redirecting to eBay for authentication.", "info")
    return redirect(build_auth_url())

@app.route("/ebay/callback")
def ebay_callback():
    auth_code = request.args.get("code")
    try:
        logging.info(f"Received auth code: {auth_code}")
        user_token = get_user_token(auth_code)
        if user_token:
            logging.info("User token obtained successfully.")
            session["user_token"] = user_token
            return redirect(url_for("index"))
        else:
            logging.warning("Failed to obtain user token.")
            flash("Failed to get user token from eBay.")
            return redirect(url_for("index"))
    except Exception as e:
        logging.error(f"Error during eBay authentication: {e}")
        flash(f"Error during eBay authentication: {e}")
        return redirect(url_for("index"))

@app.route("/ebay-connect", methods=["GET", "POST"])
def ebay_connect():
    if request.method == "POST":
        update_ebay_data()
        return jsonify({"status": "success", "message": "Data updated successfully"})
    return render_template("ebay-connect.html")

def update_ebay_data():
    user_token = session.get("user_token")
    if not user_token:
        print("ユーザートークンが存在しません。")
        return
    
    # eBay APIの設定と処理（既存のコードをそのまま使用）
    # ...

@app.route("/active-listings", methods=["GET", "POST"])
def active_listings():
    client = datastore.Client()
    user_id = user_ebay_data(user_token=session.get("user_token"))

    page_limit = 30
    start_cursor = request.args.get("cursor", None)
    if start_cursor:
        start_cursor = base64.urlsafe_b64decode(start_cursor.encode("utf-8"))

    query = client.query(kind=f"EbayItem_{user_id}")
    query_iter = query.fetch(limit=page_limit, start_cursor=start_cursor)

    ebay_items = list(query_iter)

    next_cursor = query_iter.next_page_token
    if next_cursor:
        next_cursor = base64.urlsafe_b64encode(next_cursor).decode("utf-8")

    return render_template(
        "active_listings.html", listings=ebay_items, next_cursor=next_cursor
    )


@app.route("/generate-gpt-title", methods=["POST"])
def generate_gpt_title_endpoint():
    data = request.get_json()
    gpt_description = data.get("gpt_description")
    if not gpt_description:
        return jsonify(status="error", message="Item description is missing."), 400

# 新しいAPIエンドポイント
@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    transactions = Transaction.query.all()
    return jsonify([{
        'id': t.id,
        'date': t.date.isoformat(),
        'platform': t.platform,
        'product_name': t.product_name,
        'sale_amount': t.sale_amount,
        'purchase_cost': t.purchase_cost,
        'shipping_cost': t.shipping_cost,
        'profit': t.profit
    } for t in transactions])

@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.json
    new_transaction = Transaction(
        date=datetime.fromisoformat(data['date']),
        platform=data['platform'],
        product_name=data['product_name'],
        sale_amount=data['sale_amount'],
        purchase_cost=data['purchase_cost'],
        shipping_cost=data['shipping_cost'],
        profit=data['sale_amount'] - data['purchase_cost'] - data['shipping_cost']
    )
    db.session.add(new_transaction)
    db.session.commit()
    return jsonify({'message': 'Transaction added successfully'}), 201

@app.route('/api/summary', methods=['GET'])
def get_summary():
    total_sales = db.session.query(db.func.sum(Transaction.sale_amount)).scalar() or 0
    total_profit = db.session.query(db.func.sum(Transaction.profit)).scalar() or 0
    total_listings = Transaction.query.count()
    return jsonify({
        'total_sales': total_sales,
        'total_profit': total_profit,
        'total_listings': total_listings
    })

@app.route('/api/fetch_ebay_data', methods=['POST'])
def fetch_ebay_data():
    # eBayデータ取得ロジックを実装
    # ...
    return jsonify({'message': 'eBay data fetched and saved successfully'}), 200

@app.route('/api/financial-data')
def fetch_financial_data():
    user_token = session.get("user_token")
    if not user_token:
        return jsonify({"error": "User not authenticated"}), 401

    start_date = request.args.get('start_date', None)
    end_date = request.args.get('end_date', None)

    try:
        financial_data = get_financial_data(user_token, start_date, end_date)
        return jsonify(financial_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)