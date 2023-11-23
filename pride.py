import os
import requests
from requests.auth import HTTPBasicAuth
from ebaysdk.trading import Connection as Trading
from ebaysdk.exception import ConnectionError
import json

# eBayのAPIキー

app_id = "shunkiku-tooltest-PRD-690cb6562-fcc8791f"
dev_id = "8480f8f3-218c-48ff-bd22-0a6787809783"
cert_id = "PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b"

print("App ID:", app_id)
print("Dev ID:", dev_id)
print("Cert ID:", cert_id)


def get_new_oauth_token(app_id, cert_id):
    url = "https://api.ebay.com/identity/v1/oauth2/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",  # または必要なスコープに応じて調整
    }
    response = requests.post(
        url, headers=headers, data=data, auth=HTTPBasicAuth(app_id, cert_id)
    )

    if response.status_code == 200:
        return json.loads(response.text)["access_token"]
    else:
        raise Exception("Failed to get new OAuth token")


# 新しいトークンの取得
new_token = get_new_oauth_token(app_id, cert_id)

print("New token:", new_token)


def save_price_data(data, filename="price_data.json"):
    with open(filename, "w") as file:
        json.dump(data, file)


def load_price_data(filename="price_data.json"):
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# eBay APIの初期化
api = Trading(
    appid=app_id, devid=dev_id, certid=cert_id, token=new_token, config_file=None
)

print("API:", api)

response = api.execute(
    "GetMyeBaySelling", {"ActiveList": True, "DetailLevel": "ReturnAll"}
)

print("Response:", response.dict())


def fetch_current_listings(api):
    app_id = "shunkiku-tooltest-PRD-690cb6562-fcc8791f"
    dev_id = "8480f8f3-218c-48ff-bd22-0a6787809783"
    cert_id = "PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b"

    api = Trading(
        appid=app_id,
        devid=dev_id,
        certid=cert_id,
        token=new_token,
        config_file=None,
    )
    response = api.execute(
        "GetMyeBaySelling", {"ActiveList": True, "DetailLevel": "ReturnAll"}
    )
    if response.reply.Ack == "Success" and hasattr(response.reply, "ActiveList"):
        return response.reply.ActiveList.ItemArray.Item
    else:
        return None


def update_price(api, item_id, current_price):
    new_price = current_price - 1  # 1ドル減額
    response = api.execute(
        "ReviseItem", {"Item": {"ItemID": item_id, "StartPrice": new_price}}
    )
    if response.reply.Ack == "Success" and hasattr(response.reply, "ActiveList"):
        return response.reply.ActiveList.ItemArray.Item
    else:
        return None


current_listings = fetch_current_listings(api)

# 各リスティングに対して価格調整を行う
price_data = load_price_data()

if current_listings:
    for item in current_listings:
        item_id = item.ItemID
        current_price = float(item.SellingStatus.CurrentPrice.value)

        if item_id not in price_data:
            price_data[item_id] = {"initial_price": current_price, "decrements": 0}

        new_price = current_price - 1
        price_data[item_id]["decrements"] += 1

        if new_price >= 1:
            if not update_price(api, item_id, new_price):
                print(
                    f"Failed to decrease price for Item ID: {item_id}, reverting to initial price."
                )
                update_price(api, item_id, price_data[item_id]["initial_price"])
            else:
                print(f"Price decreased for Item ID: {item_id} to {new_price}")
        else:
            print(
                f"No update needed for Item ID: {item_id} as it is already at or below minimum threshold"
            )

save_price_data(price_data)
