# import openai
# import os
# from openai import OpenAI

# client = OpenAI()
# openai.api_key = os.environ.get("OPENAI_API_KEY")


# def gpt4vision(image_url, item_id):
#     """
#     画像からテキストを生成します。
#     :param image_url: 画像のURL
#     """
#     item_id = item_id
#     response_img = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         messages=[
#             {
#                 "role": "user",
#                 "content": [
#                     {"type": "text", "text": "What’s in this image?"},
#                     {
#                         "type": "image_url",
#                         "image_url": {
#                             "url": image_url,
#                         },
#                     },
#                 ],
#             }
#         ],
#         max_tokens=300,
#     )
#     gpt_img_description = response_img.choices[0].message.content
#     return gpt_img_description


# descriptions = {}  # 結果を格納する辞書

# # 結果の確認
# for item_id, image_url in item_images.items():
#     description = gpt4vision(image_url, item_id)
#     descriptions[item_id] = description

# # 結果の確認
# for item_id, description in descriptions.items():
#     print(f"商品ID: {item_id}, 画像説明: {description}")
#     # GPT関数の適用

# from google.cloud import datastore

# # Datastoreクライアントの初期化
# client = datastore.Client()
# kind = "EbayItem"  # 使用するKind

# for item_id, description in descriptions.items():
#     key = client.key(kind, item_id)  # Datastoreのキーを作成（既存のエンティティを更新する場合）
#     entity = client.get(key) or datastore.Entity(key=key)  # エンティティを取得（存在しない場合は新規作成）
#     entity["image_description"] = description  # エンティティに画像説明を追加
#     client.put(entity)  # エンティティをDatastoreに保存

# print("画像説明をDatastoreに保存しました。")


# def gpt4_img_to_title(description, item_id):
#     item_id = item_id
#     client = OpenAI()

#     response_title_img = client.chat.completions.create(
#         model="gpt-4-vision-preview",
#         messages=[
#             {
#                 "role": "system",
#                 "content": "You are an excellent eBay top seller who is well-versed in eBay's algorithm and capable of creating highly effective titles",
#             },
#             {
#                 "role": "user",
#                 "content": description
#                 + "Optimize This Title for eBay's Algorithm in Less Than 80 Characters.",
#             },
#         ],
#     )

#     generated_title = response_title_img.choices[0].message.content
#     return generated_title


# response_title = client.chat.completions.create(
#     model="gpt-4-vision-preview",
#     messages=[
#         {
#             "role": "system",
#             "content": "You are an excellent eBay top seller who is well-versed in eBay's algorithm and capable of creating highly effective titles",
#         },
#         {
#             "role": "user",
#             "content": item_title
#             + "Optimize This Title for eBay's Algorithm in Less Than 80 Characters.",
#         },
#     ],
# )

# # 応答オブジェクトから 'content' を抽出
# content = response_title.choices[0].message.content
# print("テキストタイトル", content)


# # def get_item_info(api, item_id):
# #     """
# #     商品のItem Specifics description 画像を取得します。

# #     :param api: Trading APIのインスタンス
# #     :param item_id: 取得する商品のID
# #     """

# #     request = {
# #         "ItemID": item_id,
# #         "DetailLevel": "ReturnAll",
# #         "IncludeItemSpecifics": "true",
# #     }

# #     get_item_info_response = api.execute("GetItem", request)
# #     item_info = get_item_info_response.dict()
# #     item_specifics = (
# #         item_info.get("Item", {}).get("ItemSpecifics", {}).get("NameValueList", [])
# #     )
# #     item_description = item_info.get("Item", {}).get("Description", "")
# #     item_imgurl = (
# #         item_info.get("Item", {}).get("PictureDetails", {}).get("PictureURL", [])
# #     )
# #     return item_specifics, item_description, item_imgurl


# # print(get_item_info(api, item_id))


# def get_item_price(item_id):
#     """
#     商品のItem Specifics description 画像を取得します。

#     :param api: Trading APIのインスタンス
#     :param item_id: 取得する商品のID
#     """
#     api = Trading(
#         domain="api.ebay.com",
#         config_file=None,
#         appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",
#         devid="8480f8f3-218c-48ff-bd22-0a6787809783",
#         certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",
#         token="v^1.1#i^1#f^0#I^3#p^3#r^0#t^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",
#         siteid="0",
#     )

#     request = {
#         "ItemID": item_id,
#         "DetailLevel": "ReturnAll",
#         "IncludeItemSpecifics": "true",
#     }

#     get_item_info_response = api.execute("GetItem", request)
#     item_info = get_item_info_response.dict()
#     # 価格
#     item_price = (
#         item_info.get("Item", {})
#         .get("SellingStatus", {})
#         .get("CurrentPrice", {})
#         .get("value", [])
#     )
#     return item_price


# print(get_item_price(item_id))
