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


from bs4 import BeautifulSoup


def update_html_description(html_code, new_text):
    """
    HTMLの説明文を更新する関数。
    :param html_code: 更新するHTMLコード
    :param new_text: 挿入する新しいテキスト
    :return: 更新されたHTMLコード
    """
    # BeautifulSoupオブジェクトを作成
    soup = BeautifulSoup(html_code, "html.parser")
    # "Item Title"の<h2>タグを見つける
    item_title_tag = soup.find("h2", text="Item Title")

    # "Description"の新しい<h2>タグを作成
    new_h2_tag = soup.new_tag("h2")
    new_h2_tag.string = "Description"

    # "Item Title"の<h2>タグの直後のテキストノードを見つける
    item_title_text = item_title_tag.next_sibling

    # "Description"の新しい<h2>タグと任意のテキストを挿入
    item_title_text.insert_after(new_h2_tag)
    new_h2_tag.insert_after(new_text)  # 新しいテキストを追加
    # 変更されたHTMLを文字列として返す
    return str(soup)


# html_code = "<div class='main1'><h2>Item Title</h2></div>"
# new_text = "ここに新しい説明文を挿入"
# updated_html = update_html_description(html_code, new_text)
# print(updated_html)


def final_html_description(item_id, user_id, pre_description):
    """
    HTMLの説明文を更新する関数。
    :param html_code: 更新するHTMLコード
    :param new_text: 挿入する新しいテキスト
    :return: 更新されたHTMLコード
    """
    # BeautifulSoupオブジェクトを作成
    client = datastore.Client()
    item_id_str = str(item_id)
    user_id_str = str(user_id)
    key = client.key(f"EbayItem_{user_id_str}", item_id_str)
    print(key)
    entity = client.get(key)
    description = entity.get("Description") if entity else None
    print(description)

    soup = BeautifulSoup(description, "html.parser")
    # "Item Title"の<h2>タグを見つける
    item_title_tag = soup.find("h2", text="Item Title")

    # "Description"の新しい<h2>タグを作成
    new_h2_tag = soup.new_tag("h2")
    new_h2_tag.string = "Description"

    # "Item Title"の<h2>タグの直後のテキストノードを見つける
    item_title_text = item_title_tag.next_sibling

    # "Description"の新しい<h2>タグと任意のテキストを挿入
    item_title_text.insert_after(new_h2_tag)
    new_h2_tag.insert_after(pre_description)  # 新しいテキストを追加
    # 変更されたHTMLを文字列として返す
    return str(soup)


import traceback


def revise_item_description(user_token, item_id, new_description):
    """
    eBayの商品説明を更新します。
    :param user_token: eBayのユーザートークン
    :param item_id: 更新する商品のID
    :param new_description: 新しい商品説明
    """
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
            "Description": """<![CDATA[
                <meta charset="utf-8" /><meta   name="viewport"   content="width=device-width&#044; initial-scale=1" /><style>   .main1 {     border: 1px solid #000;     border-radius: 5px;     margin: 0 auto;     width: 100%;     padding: 0 20px 10px;     background: #fff;     box-sizing: border-box;     word-break: break-all;   }   .main1 p,   .main1 span {     line-height: 24px;     font-size: 18px;   }   .main1 h1 {     font-size: 26px !important;     margin: 30px 0;     text-align: center;     color: #000;   }   .main1 h2 {     margin: 0 0 10px 0;     color: #000;     font-size: 22px;     line-height: 1.2;     text-align: left;   }   .main1 p,   .main1 .product_dec div {     margin: 0;     padding: 0 0 20px 0;     color: #333;     text-align: left;   }   .margin-bottom_change {     padding-bottom: 10px !important;   }   h2 {     border-left: 5px solid #1190d9;     background-color: #f1f1f1;     padding: 10px 20px;   } </style> """
            + new_description
            + "]]>",
        }
    }

    try:
        response = api.execute("ReviseItem", request)

        # eBay APIの応答の詳細をログに出力
        print("eBay API Response:", response.dict())

        if response.reply.Ack != "Failure":
            return {
                "success": True,
                "message": "The item description has been updated successfully.",
            }
        else:
            return {
                "success": False,
                "message": "Failed to update the item description.",
                "error_details": response.reply.Errors,
            }
    except Exception as e:
        # スタックトレースを出力
        traceback.print_exc()
        return {
            "success": False,
            "message": "An exception occurred while updating the item description.",
            "error_details": str(e),
        }


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


def user_ebay_data(user_token):
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
    response_user = api.execute("GetUser", {})
    user_data = response_user.dict()
    user_id = user_data["User"]["UserID"]
    return user_id


from openai import OpenAI

client = OpenAI()


def gpt4vision(image_url):
    client = OpenAI()
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    response_img = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What’s in this image?"},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=500,
    )
    gpt_img_description = response_img.choices[0].message.content
    return gpt_img_description


def gpt4_img_to_title(gpt_description):
    client = OpenAI()
    openai.api_key = os.environ.get("OPENAI_API_KEY")

    formatted_description = f"""
    {gpt_description}
    Optimize This Title for eBay's Algorithm in Less Than 80 Characters.
    """

    response_title_img = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "system",
                "content": "You are an excellent eBay top seller who is well-versed in eBay's algorithm and capable of creating highly effective titles",
            },
            {
                "role": "user",
                "content": formatted_description
                + "Optimize This Title for eBay's Algorithm in Less Than 80 Characters.",
            },
        ],
    )

    generated_title = response_title_img.choices[0].message.content
    return generated_title
