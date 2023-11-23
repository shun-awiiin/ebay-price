import os
import requests
from requests.auth import HTTPBasicAuth
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import json
import xml.etree.ElementTree as ET

# eBayのAPIキー

app_id = "shunkiku-tooltest-PRD-690cb6562-fcc8791f"
dev_id = "8480f8f3-218c-48ff-bd22-0a6787809783"
cert_id = "PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b"


def initialize_ebay_api(app_id, dev_id, cert_id, token):
    """
    Initialize the eBay Trading API.
    """
    return Trading(
        appid=app_id, devid=dev_id, certid=cert_id, token=token, config_file=None
    )


def get_new_oauth_token(app_id, cert_id):
    """
    Obtain a new OAuth token.
    """
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    try:
        response = requests.post(
            url, headers=headers, data=data, auth=HTTPBasicAuth(app_id, cert_id)
        )
        response.raise_for_status()
        return json.loads(response.text)["access_token"]
    except requests.RequestException as e:
        raise ConnectionError("Failed to get new OAuth token: " + str(e))


token = get_new_oauth_token(app_id, cert_id)
print(token)


def fetch_current_listings(token):
    """
    Fetch current listings from eBay.
    """
    url = "https://api.ebay.com/ws/api.dll"
    headers = {
        "Content-Type": "text/xml",
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": "GetMyeBaySelling",
        "Authorization": f"Bearer {token}",
    }
    body = """<?xml version="1.0" encoding="utf-8"?>
    <GetMyeBaySellingRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials>
            <eBayAuthToken>{}</eBayAuthToken>
        </RequesterCredentials>
        <ActiveList>
            <Include>true</Include>
        </ActiveList>
    </GetMyeBaySellingRequest>""".format(
        token
    )

    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()

    # 解析するXMLを取得
    root = ET.fromstring(response.content)

    # 応答から必要なデータを抽出
    items = []
    for item in root.findall(".//Item"):
        item_id = item.find("ItemID").text
        current_price = float(item.find("SellingStatus/CurrentPrice").text)
        items.append({"ItemID": item_id, "CurrentPrice": current_price})

    return items


# 現在のリストの取得
listings = fetch_current_listings(token)
print(listings)


def update_price(token, item_id, new_price):
    """
    Update the price of a listed item using a direct HTTP request.
    """
    url = "https://api.ebay.com/ws/api.dll"
    headers = {
        "Content-Type": "text/xml",
        "X-EBAY-API-SITEID": "0",
        "X-EBAY-API-COMPATIBILITY-LEVEL": "967",
        "X-EBAY-API-CALL-NAME": "ReviseItem",
        "Authorization": f"Bearer {token}",
    }
    body = """<?xml version="1.0" encoding="utf-8"?>
    <ReviseItemRequest xmlns="urn:ebay:apis:eBLBaseComponents">
        <RequesterCredentials>
            <eBayAuthToken>{}</eBayAuthToken>
        </RequesterCredentials>
        <Item>
            <ItemID>{}</ItemID>
            <StartPrice>{}</StartPrice>
        </Item>
    </ReviseItemRequest>""".format(
        token, item_id, new_price
    )
    response = requests.post(url, headers=headers, data=body)
    response.raise_for_status()

    # 応答の解析
    root = ET.fromstring(response.content)

    # 成功したかどうかを確認
    if root.find(".//Ack").text != "Success":
        raise Exception(f"Failed to update price for Item ID: {item_id}")
    try:
        response = requests.post(url, headers=headers, data=body)
        response.raise_for_status()
        # 応答の解析と成功確認が必要
    except requests.RequestException as e:
        print(f"Error in updating price for Item ID {item_id}: {e}")


def main():
    """
    Main function to execute the eBay price updating logic.
    """
    token = get_new_oauth_token(app_id, cert_id)
    current_listings = fetch_current_listings(
        token
    )  # fetch_current_listingsは直接リクエストに基づいていると仮定

    if current_listings:
        for item in current_listings:
            item_id = item["ItemID"]  # 応答の形式に応じて変更
            current_price = float(item["CurrentPrice"])  # 応答の形式に応じて変更
            new_price = max(current_price - 1, 1)  # Ensure price doesn't go below 1
            update_price(token, item_id, new_price)


if __name__ == "__main__":
    main()
