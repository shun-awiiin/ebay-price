# # ////FINDINGAPI/////
# # import requests
# # import json

# # # Finding APIのエンドポイント
# # FINDING_API_ENDPOINT = "https://svcs.ebay.com/services/search/FindingService/v1"

# # # APIリクエストのパラメータ
# # params = {
# #     "OPERATION-NAME": "findItemsByKeywords",
# #     "SERVICE-VERSION": "1.0.0",
# #     "SECURITY-APPNAME": "shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # ここにあなたのAppIDを入れてください
# #     "RESPONSE-DATA-FORMAT": "JSON",
# #     "keywords": "Pokemon",  # ここに検索したいキーワードを入れてください
# # }

# # # APIリクエストを実行
# # response = requests.get(FINDING_API_ENDPOINT, params=params)

# # # レスポンスをJSON形式で取得
# # response_json = response.json()

# # # 結果を整形して表示
# # # print(json.dumps(response_json, indent=2, ensure_ascii=False))


# # # Finding APIのレスポンスから商品リストを整形して表示する関数を定義します。
# # def display_search_results(response_json):
# #     if response_json.get("findItemsByKeywordsResponse"):
# #         search_response = response_json["findItemsByKeywordsResponse"][0]
# #         if search_response.get("ack") == ["Success"]:
# #             search_result = search_response.get("searchResult", [{}])[0]
# #             item_count = search_result.get("@count", 0)
# #             items = search_result.get("item", [])

# #             print(f"Total items found: {item_count}")
# #             for item in items:
# #                 title = item.get("title", ["N/A"])[0]
# #                 category_name = item.get("primaryCategory", [{}])[0].get(
# #                     "categoryName", ["N/A"]
# #                 )[0]
# #                 gallery_url = item.get("galleryURL", ["N/A"])[0]
# #                 view_item_url = item.get("viewItemURL", ["N/A"])[0]

# #                 print(f"Title: {title}")
# #                 print(f"Category: {category_name}")
# #                 print(f"Gallery URL: {gallery_url}")
# #                 print(f"View Item URL: {view_item_url}")
# #                 print("-" * 50)
# #         else:
# #             print("No items found or an error occurred.")
# #     else:
# #         print("Invalid response format.")


# # # Finding APIのレスポンスを再度取得します（以前のコードブロックで取得したレスポンスを使用します）。
# # # ここでは、以前のレスポンスを再利用するため、APIリクエストを再度実行する必要はありません。
# # response_json = response.json()

# # # 商品の検索結果を表示
# # display_search_results(response_json)


# # ////ShoppingAPI/////

# # import requests
# # import json

# # # Shopping APIのエンドポイント
# # SHOPPING_API_ENDPOINT = "https://open.api.ebay.com/shopping"

# # # アクセストークン
# # ACCESS_TOKEN = "v^1.1#i^1#f^0#I^3#p^3#r^0#t^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"  # 実際のアクセストークンに置き換えてください

# # # APIリクエストのヘッダー
# # headers = {"X-EBAY-API-IAF-TOKEN": ACCESS_TOKEN}

# # # APIリクエストのパラメータ
# # params = {
# #     "callname": "GetSingleItem",
# #     "responseencoding": "JSON",
# #     "appid": "shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # ここにあなたのAppIDを入れてください
# #     "siteid": "0",
# #     "version": "967",
# #     "ItemID": "274289514411",  # ここに検索したい商品IDを入れてください
# # }

# # # APIリクエストを実行
# # response = requests.get(SHOPPING_API_ENDPOINT, headers=headers, params=params)

# # # レスポンスをJSON形式で取得
# # response_json = response.json()

# # # 結果を整形して表示
# # # print(json.dumps(response_json, indent=2, ensure_ascii=False))


# # # 取得したJSONデータから重要な情報を抽出して表示する関数を定義します。
# # def display_item_details(response_json):
# #     if response_json.get("Ack") == "Success" and "Item" in response_json:
# #         item = response_json["Item"]
# #         title = item.get("Title")
# #         price = (
# #             item.get("ConvertedCurrentPrice", {}).get("Value")
# #             if item.get("ConvertedCurrentPrice")
# #             else "N/A"
# #         )
# #         currency = (
# #             item.get("ConvertedCurrentPrice", {}).get("CurrencyID")
# #             if item.get("ConvertedCurrentPrice")
# #             else "N/A"
# #         )
# #         location = item.get("Location")
# #         gallery_url = item.get("GalleryURL")
# #         view_item_url = item.get("ViewItemURLForNaturalSearch")

# #         print(f"Title: {title}")
# #         print(f"Price: {price} {currency}")
# #         print(f"Location: {location}")
# #         print(f"Gallery URL: {gallery_url}")
# #         print(f"View Item URL: {view_item_url}")
# #     else:
# #         print("Item details not found or an error occurred.")


# # # レスポンスをJSON形式で取得
# # response_json = response.json()

# # # 商品の詳細情報を表示
# # display_item_details(response_json)

# # Merchandising APIのエンドポイント

# import requests

# MERCHANDISING_API_ENDPOINT = "https://svcs.ebay.com/MerchandisingService"

# # 'getMostWatchedItems'操作のリクエストパラメータ
# params = {
#     "OPERATION-NAME": "getMostWatchedItems",
#     "SERVICE-NAME": "MerchandisingService",
#     "SERVICE-VERSION": "1.1.0",
#     "CONSUMER-ID": "shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # ここにあなたのAppIDを入れてください
#     "RESPONSE-DATA-FORMAT": "JSON",
#     "REST-PAYLOAD": "",
#     "maxResults": "50",  # 取得するアイテムの最大数
#     "categoryId": "20081",  # カテゴリーID（Books）
# }


# # APIリクエストを実行
# response = requests.get(MERCHANDISING_API_ENDPOINT, params=params)

# # レスポンスをJSON形式で取得
# response_json = response.json()

# # 結果を表示
# response_json


# # Merchandising APIの結果を綺麗に表示する関数を定義します。
# def display_most_watched_items(response_json):
#     if response_json.get("getMostWatchedItemsResponse"):
#         items_response = response_json["getMostWatchedItemsResponse"]
#         if items_response.get("ack") == "Success":
#             items = items_response.get("itemRecommendations", {}).get("item", [])
#             for item in items:
#                 title = item.get("title")
#                 watch_count = item.get("watchCount")
#                 price = item.get("buyItNowPrice", {}).get("__value__")
#                 currency = item.get("buyItNowPrice", {}).get("@currencyId")
#                 item_url = item.get("viewItemURL")
#                 image_url = item.get("imageURL")

#                 print(f"Title: {title}")
#                 print(f"Watch Count: {watch_count}")
#                 print(f"Price: {price} {currency}")
#                 print(f"Item URL: {item_url}")
#                 print(f"Image URL: {image_url}")
#                 print("-" * 80)
#         else:
#             print("No items found or an error occurred.")
#     else:
#         print("Invalid response format.")


# # 結果を綺麗に表示
# display_most_watched_items(response_json)


# # # 'getRelatedCategoryItems'操作のリクエストパラメータ
# # related_params = {
# #     "OPERATION-NAME": "getRelatedCategoryItems",
# #     "SERVICE-NAME": "MerchandisingService",
# #     "SERVICE-VERSION": "1.1.0",
# #     "CONSUMER-ID": "shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # ここにあなたのAppIDを入れてください
# #     "RESPONSE-DATA-FORMAT": "JSON",
# #     "REST-PAYLOAD": "",
# #     "itemId": "353072963766",  # 関連する商品のitemId
# #     "maxResults": "10",  # 取得するアイテムの最大数
# # }

# # # APIリクエストを実行
# # related_response = requests.get(MERCHANDISING_API_ENDPOINT, params=related_params)

# # # レスポンスをJSON形式で取得
# # related_response_json = related_response.json()

# # # 結果を表示
# # related_response_json


# ##ライバルセラーリサーチ
# # from ebaysdk.trading import Connection as Trading
# # from datetime import datetime, timedelta

# # # Calculate the time range for the listings
# # start_time_from = datetime.utcnow() - timedelta(days=120)  # 120 days ago from now
# # start_time_to = datetime.utcnow() - timedelta(days=1)  # Until yesterday

# # # Format the dates in the eBay API date format
# # start_time_from = start_time_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")
# # start_time_to = start_time_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# # セラーの出品リストを取得するためのリクエストパラメータ
# request = {
#     "DetailLevel": "ReturnAll",
#     "IncludeWatchCount": True,
#     "Pagination": {"EntriesPerPage": 100, "PageNumber": 1},
#     "StartTimeFrom": start_time_from,  # 開始日時を指定
#     "StartTimeTo": start_time_to,
#     "UserID": "clada95",
# }

# # # Trading APIへの接続設定
# # api = Trading(
# #     domain="api.ebay.com",
# #     config_file=None,
# #     appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # あなたのAppIDを入れてください
# #     devid="8480f8f3-218c-48ff-bd22-0a6787809783",  # あなたのDevIDを入れてください
# #     certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",  # あなたのCertIDを入れてください
# #     token="v^1.1#i^1#f^0#I^3#p^3#r^0#t^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",  # あなたのユーザートークンを入れてください
# #     siteid="0",
# # )

# # # APIリクエストを実行してセラーの出品リストを取得
# # response = api.execute("GetSellerList", request)

# # # レスポンスをJSON形式で取得
# # response_dict = response.dict()

# # # 結果を表示
# # response_dict

# # # APIのレスポンスデータが格納されていると仮定するresponse_dict変数があるとします

# # # レスポンスに期待するデータが含まれているか確認します
# # if response_dict.get("Ack") == "Success" and "ItemArray" in response_dict:
# #     items = response_dict["ItemArray"]["Item"]

# #     # 各アイテムの詳細を出力します
# #     for item in items:
# #         title = item.get("Title")
# #         item_id = item.get("ItemID")
# #         category_name = item.get("PrimaryCategory", {}).get("CategoryName")
# #         current_price = (
# #             item.get("SellingStatus", {}).get("CurrentPrice", {}).get("value")
# #         )
# #         currency = (
# #             item.get("SellingStatus", {}).get("CurrentPrice", {}).get("_currencyID")
# #         )
# #         listing_status = item.get("SellingStatus", {}).get("ListingStatus")
# #         watch_count = item.get("WatchCount", "N/A")

# #         print(f"タイトル: {title}")
# #         print(f"商品ID: {item_id}")
# #         print(f"カテゴリー: {category_name}")
# #         print(f"現在の価格: {current_price} {currency}")
# #         print(f"リスティングの状態: {listing_status}")
# #         print(f"ウォッチ数: {watch_count}")
# #         print("-" * 80)
# # else:
# #     print("商品が見つからないか、エラーが発生しました。")


# # from ebaysdk.trading import Connection as Trading
# # from datetime import datetime, timedelta

# # start_time_from = datetime.utcnow() - timedelta(days=120)  # 120 days ago from now
# # start_time_to = datetime.utcnow() - timedelta(days=1)  # Until yesterday

# # # Format the dates in the eBay API date format
# # start_time_from = start_time_from.strftime("%Y-%m-%dT%H:%M:%S.000Z")
# # start_time_to = start_time_to.strftime("%Y-%m-%dT%H:%M:%S.000Z")

# # # Trading APIへの接続設定
# # api = Trading(
# #     domain="api.ebay.com",
# #     config_file=None,
# #     appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # あなたのAppIDを入れてください
# #     devid="8480f8f3-218c-48ff-bd22-0a6787809783",  # あなたのDevIDを入れてください
# #     certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",  # あなたのCertIDを入れてください
# #     token="v^1.1#i^1#f^0#I^3#p^3#r^0#t^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",  # あなたのユーザートークンを入れてください
# #     siteid="0",
# # )

# # # 全商品を取得するためのループ
# # all_items = []
# # page_number = 1
# # entries_per_page = 48
# # total_pages = 10  # 初期値は1ページと仮定

# # while page_number <= total_pages:
# #     # セラーの出品リストを取得するためのリクエストパラメータ
# #     request = {
# #         "DetailLevel": "ReturnAll",
# #         "IncludeWatchCount": True,
# #         "Pagination": {"EntriesPerPage": entries_per_page, "PageNumber": page_number},
# #         "StartTimeFrom": (datetime.utcnow() - timedelta(days=120)).strftime(
# #             "%Y-%m-%dT%H:%M:%S.000Z"
# #         ),
# #         "StartTimeTo": start_time_to,
# #         "UserID": "clada95",
# #     }

# #     # APIリクエストを実行してセラーの出品リストを取得
# #     response = api.execute("GetSellerList", request)
# #     response_dict = response.dict()

# #     print(f"現在のページ: {page_number}")
# #     print(f"総ページ数: {total_pages}")

# #     # レスポンスから商品情報を取得
# #     if response_dict.get("Ack") == "Success":
# #         all_items.extend(response_dict["ItemArray"]["Item"])
# #         total_pages = int(response_dict["PaginationResult"]["TotalNumberOfPages"])
# #         page_number += 1
# #     else:
# #         # エラーが発生した場合はループを抜ける
# #         print("エラーが発生しました。")
# #         break


# # # 全商品の情報を表示
# # # 全商品の情報を整形して表示
# # for item in all_items:
# #     print(f"タイトル: {item.get('Title', 'N/A')}")


# # カテゴリーNo.取得


# # from ebaysdk.trading import Connection as Trading

# # # Trading APIへの接続設定
# # api = Trading(
# #     domain="api.ebay.com",
# #     config_file=None,
# #     appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",  # あなたのAppIDを入れてください
# #     devid="8480f8f3-218c-48ff-bd22-0a6787809783",  # あなたのDevIDを入れてください
# #     certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",  # あなたのCertIDを入れてください
# #     token="v^1.1#i^1#f^0#p^3#I^3#r^0#t^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",  # あなたのユーザートークンを入れてください
# #     siteid="0",
# # )


# # # カテゴリー情報を取得するためのリクエストパラメータ
# # request = {"DetailLevel": "ReturnAll", "LevelLimit": 1}  # トップレベルのカテゴリーのみを取得する場合

# # # APIリクエストを実行してカテゴリー情報を取得
# # response = api.execute("GetCategories", request)
# # response_dict = response.dict()

# # # カテゴリー情報を表示
# # for category in response_dict["CategoryArray"]["Category"]:
# #     print(f"カテゴリー名: {category['CategoryName']}")
# #     print(f"カテゴリーID: {category['CategoryID']}")
