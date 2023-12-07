# # 必要なライブラリと設定をインポート
from ebaysdk.trading import Connection as Trading
import pandas as pd
from google.cloud import datastore

#API接続の設定
api = Trading(
    domain="api.ebay.com",
    config_file=None,
    appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",
    devid="8480f8f3-218c-48ff-bd22-0a6787809783",
    certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",
    token="v^1.1#i^1#f^0#p^3#r^0#I^3#t^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",
    siteid="0",
)
# APIリクエストの作成
request = {
    "DetailLevel": "ReturnAll",
    "Pagination": {"EntriesPerPage": 100, "PageNumber": 1},
    "EndTimeFrom": "2023-11-01T00:00:00",
    "EndTimeTo": "2023-12-31T23:59:59",
}

# APIコールを実行して応答を取得
get_seller_list_response = api.execute("GetSellerList", request)
# 応答を辞書形式で取得
response_dict = get_seller_list_response.dict()

# client = datastore.Client()  # Google Cloud Datastoreクライアントの初期化
# SELECTED_ITEMS_KEY = "selected_items"  # 一括更新される商品IDを保存するキー


# kind = "ItemDetails"  # DatastoreのKind
# for item in response_dict.get("ItemArray", {}).get("Item", []):
#     # print(response_dict.get("ItemArray", {}).get("Item", []))
#     item_id = item.get("ItemID")
#     if not item_id:
#         continue  # 商品IDがない場合はスキップ

#     # Datastoreに保存するデータを整理
#     item_data = {
#         "ItemID": item_id,
#         "Title": item.get("Title"),
#         "Price": item.get("SellingStatus", {}).get("CurrentPrice", {}).get("value"),
#         "PictureURL": item.get("PictureDetails", {}).get("PictureURL"),
#         # 他に必要なデータがあればここに追加
#     }
#     # Datastoreに保存
#     key = client.key("EbayItem", item_id)
#     entity = datastore.Entity(key=key)
#     entity.update(item_data)
#     client.put(entity)

# # 商品情報を取得するための関数
# # 取得したエンティティからIDを抽出して表示
# for entity in results:
#     item_id = entity.get("ItemID")  # 商品ID属性
#     title = entity.get("Title")  # タイトル属性
#     price = entity.get("Price")  # 価格属性
#     image_urls = entity.get("PictureURL")  # 画像URL属性

# print(f"データ取得 - ID: {item_id}, タイトル: {title}, 価格: {price}, 画像URL: {image_urls}")

# kind = "EbayItem"  # DatastoreのKind
# # 特定のKindのすべてのエンティティに対してクエリを実行
# query = client.query(kind=kind)
# results = list(query.fetch())

# item_images = {}  # 商品IDと画像URLを紐付けるための辞書

# for entity in results:
#     item_id = entity.get("ItemID")  # 商品ID属性
#     image_urls = entity.get("PictureURL")  # 画像URL属性

#     if item_id and image_urls:
#         # image_urlsがリスト形式の場合は先頭のURLを使用
#         if isinstance(image_urls, list):
#             item_images[item_id] = image_urls[0]
#         else:
#             item_images[item_id] = image_urls


# # Datastoreクライアントの初期化
# client = datastore.Client()

# kind = "EbayItem"  # 使用するKind
# query = client.query(kind=kind)  # 特定のKindのすべてのエンティティに対してクエリを実行
# results = list(query.fetch())
# # 各エンティティの画像説明を使用してタイトルを生成
# for entity in results:
#     description = entity.get("image_description")
#     if description:
#         generated_title = gpt4_img_to_title(description, entity.key.id_or_name)
#         # エンティティに生成されたタイトルを追加
#         entity["generated_title"] = generated_title
#         # エンティティをDatastoreに保存
#         client.put(entity)

# print("生成されたタイトルをDatastoreに保存しました。")


# from datetime import datetime, timedelta


# def get_seller_list_test(api, entries_per_page=100, page_number=1):
#     """
#     eBayの販売リストを取得します。
#     """
#     end_time_from = datetime.now() - timedelta(days=90)
#     end_time_to = datetime.now()

#     request = {
#         "DetailLevel": "ReturnAll",
#         "Pagination": {"EntriesPerPage": entries_per_page, "PageNumber": page_number},
#         "StartTimeFrom": end_time_from.strftime("%Y-%m-%dT%H:%M:%S"),
#         "StartTimeTo": end_time_to.strftime("%Y-%m-%dT%H:%M:%S"),
#     }
#     # フィルターオプションをリクエストに追加

#     response_seller = api.execute("GetSellerList", request)
#     seller_all = response_seller.dict()
#     seller_include = seller_all["ItemArray"]["Item"]
#     return seller_include


# print("セラー", get_seller_list_test(api))

# response_active = api.execute("GetMyeBaySelling", {"ActiveList": True})
# response_sold = api.execute("GetMyeBaySelling", {"SoldList": True})

# # アクティブリストの情報を表示
# print(df(response_active.dict()))
# item_active = response_active.dict()
# print(item_active["ActiveList"]["ItemArray"]["Item"][0])

# # 売れた商品のリストの情報を表示
# print(response_sold.dict())

# response_getmyebayselling = api.execute("GetMyeBaySelling", {})
# all_myebay = response_getmyebayselling.dict()
# print(all_myebay)
