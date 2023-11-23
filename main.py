import os
import requests
from requests.auth import HTTPBasicAuth
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

app_id = "shunkiku-tooltest-PRD-690cb6562-fcc8791f"
dev_id = "8480f8f3-218c-48ff-bd22-0a6787809783"
cert_id = "PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b"


def get_seller_list(user_token, entries_per_page=100, page_number=1):
    api = Trading(
        config_file=None,
        appid="app_id",
        devid="dev_id",
        certid="cert_id",
        token=user_token,
    )

    # 現在の日時から90日前の日時を計算
    end_time_from = datetime.now() - timedelta(days=90)
    end_time_to = datetime.now()

    request = {
        "DetailLevel": "ReturnAll",
        "Pagination": {"EntriesPerPage": entries_per_page, "PageNumber": page_number},
        "UserID": "awiiin",
        "StartTimeFrom": end_time_from.strftime("%Y-%m-%dT%H:%M:%S"),
        "StartTimeTo": end_time_to.strftime("%Y-%m-%dT%H:%M:%S"),
    }

    response = api.execute("GetSellerList", request)
    return response.dict()


# ここでユーザートークンと他の必要な詳細を提供します
seller_list = get_seller_list(user_token)


def extract_active_listings(seller_list):
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
                {"Title": title, "Item ID": item_id, "Current Price": current_price}
            )

    return active_items


# seller_listは、APIから取得した完全な出品データです。
active_seller_list = extract_active_listings(seller_list)
for item in active_seller_list:
    print(item)
