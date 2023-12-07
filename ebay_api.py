import requests
import logging
from requests.auth import HTTPBasicAuth
from ebaysdk.trading import Connection as Trading
import json
import base64
from datetime import datetime, timedelta
import openai
import os
from google.cloud import datastore


# eBayアプリケーションの設定
app_id = "shunkiku-tooltest-PRD-690cb6562-fcc8791f"
dev_id = "8480f8f3-218c-48ff-bd22-0a6787809783"
cert_id = "PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b"
redirect_uri = "shun_kikuchi-shunkiku-toolte-bfxiiub"


def build_auth_url():
    """
    eBayの認証URLを構築し、ユーザーが認証コードを取得できるようにします。
    """
    auth_url = f"https://signin.ebay.com/authorize?client_id={app_id}&response_type=code&redirect_uri={redirect_uri}&scope=https://api.ebay.com/oauth/api_scope"
    return auth_url


def get_user_token(auth_code):
    """
    eBayからユーザートークンを取得します。
    """
    url = "https://api.ebay.com/identity/v1/oauth2/token"

    # Basic認証のためのクレデンシャルのエンコード
    credentials = f"{app_id}:{cert_id}"
    encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode("utf-8")

    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }

    data = {
        "grant_type": "authorization_code",
        "code": auth_code,
        "redirect_uri": redirect_uri,
    }

    try:
        response = requests.post(url, headers=headers, data=data)
        response.raise_for_status()
        token = json.loads(response.text)["access_token"]
        logging.info("User token successfully retrieved")
        return token
    except requests.RequestException as e:
        logging.error(f"Error in getting user token: {e}")
        raise


def get_seller_list(user_token, entries_per_page=100, page_number=1):
    """
    eBayの販売リストを取得します。
    """
    api = Trading(
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
    )

    end_time_from = datetime.now() - timedelta(days=90)
    end_time_to = datetime.now()

    request = {
        "DetailLevel": "ReturnAll",
        "Pagination": {"EntriesPerPage": entries_per_page, "PageNumber": page_number},
        "StartTimeFrom": end_time_from.strftime("%Y-%m-%dT%H:%M:%S"),
        "StartTimeTo": end_time_to.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    # フィルターオプションをリクエストに追加

    response = api.execute("GetSellerList", request)
    return response.dict()


# アイテムスペシフィックスを取得する関数
def get_item_info(item_id, user_token):
    """
    商品のItem Specifics description 画像を取得します。

    :param api: Trading APIのインスタンス
    :param item_id: 取得する商品のID
    """
    api = Trading(
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
    )

    request = {
        "ItemID": item_id,
        "DetailLevel": "ReturnAll",
        "IncludeItemSpecifics": "true",
    }

    get_item_info_response = api.execute("GetItem", request)
    item_info = get_item_info_response.dict()

    item_specifics = (
        item_info.get("Item", {}).get("ItemSpecifics", {}).get("NameValueList", [])
    )
    item_description = item_info.get("Item", {}).get("Description", "")
    item_imgurl = (
        item_info.get("Item", {}).get("PictureDetails", {}).get("PictureURL", [])
    )

    return item_specifics, item_description, item_imgurl


def get_item_price(item_id, user_token):
    """
    商品のItem Specifics description 画像を取得します。

    :param api: Trading APIのインスタンス
    :param item_id: 取得する商品のID
    """
    api = Trading(
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
    )

    request = {
        "ItemID": item_id,
        "DetailLevel": "ReturnAll",
        "IncludeItemSpecifics": "true",
    }

    get_item_info_response = api.execute("GetItem", request)
    item_info = get_item_info_response.dict()
    item_data = save_item_details(item_info)

    # 価格
    item_price = (
        item_info.get("Item", {})
        .get("SellingStatus", {})
        .get("CurrentPrice", {})
        .get("value", [])
    )
    return item_price, item_data


client = datastore.Client()  # Google Cloud Datastoreクライアントの初期化
SELECTED_ITEMS_KEY = "selected_items"  # 一括更新される商品IDを保存するキー


# 商品情報を保存するための関数
def save_item_details(item_info):
    kind = "ItemDetails"  # DatastoreのKind
    logging.info("Saving item details for"(item_info))
    for item_id, details in item_info.items():
        key = client.key(kind, item_id)  # 商品IDを識別子として使用
        entity = datastore.Entity(key=key)
        entity.update(details)
        client.put(entity)


def extract_active_listings(seller_list):
    """
    販売リストからアクティブなリストを抽出します。
    """
    items = seller_list.get("ItemArray", {}).get("Item", [])
    active_items = []

    for item in items:
        if item.get("SellingStatus", {}).get("ListingStatus", "") == "Active":
            title = item.get("Title", "No Title")
            item_id = item.get("ItemID", "No Item ID")
            current_price = (
                item.get("SellingStatus", {})
                .get("CurrentPrice", {})
                .get("value", "No Price")
            )

            active_items.append(
                {
                    "Title": title,
                    "Item ID": item_id,
                    "Current Price": current_price,
                }
            )

    return active_items


def revise_item_price(user_token, item_id, new_price):
    api = Trading(
        domain="api.ebay.com",
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
        siteid="0",
    )

    request = {
        "Item": {
            "ItemID": item_id,
            "StartPrice": new_price,
        }
    }

    response = api.execute("ReviseItem", request)
    return response.dict()


def revise_item_title(user_token, item_id, new_title):
    api = Trading(
        domain="api.ebay.com",
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
        siteid="0",
    )

    request = {
        "Item": {
            "ItemID": item_id,
            "Title": new_title,
        }
    }

    response = api.execute("ReviseItem", request)
    return response.dict()


def revise_item_specifics(user_token, item_id, new_item_specifics):
    api = Trading(
        domain="api.ebay.com",
        config_file=None,
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=user_token,
        siteid="0",
    )

    request = {
        "Item": {
            "ItemID": item_id,
            "ItemSpecifics": {
                "NameValueList": [
                    {"Name": key, "Value": value}
                    for key, value in new_item_specifics.items()
                ]
            },
        }
    }

    response = api.execute("ReviseItem", request)
    return response.dict()
