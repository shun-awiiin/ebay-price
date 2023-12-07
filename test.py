from ebaysdk.trading import Connection as Trading
import pandas as pd
from google.cloud import datastore
import openai
import os
from openai import OpenAI
import ast

client = OpenAI()
openai.api_key = os.environ.get("OPENAI_API_KEY")


# API接続の設定
api = Trading(
    domain="api.ebay.com",
    config_file=None,
    appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",
    devid="8480f8f3-218c-48ff-bd22-0a6787809783",
    certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",
    token="v^1.1#i^1#p^3#I^3#f^0#r^0#t^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",
    siteid="0",
)

# 商品IDを設定
item_id = "364540394308"

# APIリクエストの作成
request = {"ItemID": item_id, "DetailLevel": "ReturnAll", "IncludeItemSpecifics": True}
# APIコールを実行して応答を取得
get_item_specifics_response = api.execute("GetItem", request)
# 応答を辞書形式で取得
response_dict = get_item_specifics_response.dict()
df = pd.DataFrame
print(df(response_dict))

# 応答からタイトルを抽出
item_title = response_dict.get("Item", {}).get("Title", "")
# 応答からItemSpecificsのみを抽出
item_specifics = (
    response_dict.get("Item", {}).get("ItemSpecifics", {}).get("NameValueList", [])
)
image_url = (
    response_dict.get("Item", {}).get("PictureDetails", {}).get("PictureURL", [])
)

# # 応答から現在価格を抽出
# current_price = (
#     response_dict.get("Item", {})
#     .get("SellingStatus", {})
#     .get("CurrentPrice", {})
#     .get("value", "")
# )

# dec_count = 1

# new_price = float(current_price) - float(dec_count)
# # 結果を出力
print("アイテム詳細", df(item_specifics))
print("画像URL", image_url)
print("商品タイトル", item_title)
# print("現在価格", current_price)
# print("新価格", new_price)

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
    max_tokens=300,
)
gpt_img_description = response_img.choices[0].message.content
print("画像説明", gpt_img_description)


def dict_to_string(d):
    return ", ".join(f"{key}: {value}" for key, value in d.items())


# リスト内の各辞書を文字列に変換し、それらを更にカンマで結合する
specifics_string = ", ".join(dict_to_string(item) for item in item_specifics)
print("文字列のスペシフィックス", specifics_string)

response_specifics = client.chat.completions.create(
    model="gpt-4-vision-preview",
    messages=[
        {
            "role": "system",
            "content": "You are an excellent eBay top seller who is well-versed in eBay's algorithm and capable of creating highly effective item specifics. I am an eBay assistant who can help you create item specifics for your listings. I will ask you a series of questions to help me understand what you are selling and what you would like to include in your item specifics.",
        },
        {
            "role": "user",
            "content": "Just say yes if you understand."
            + "I will give you a prerequisite.The prerequisite is"
            + gpt_img_description,
        },
        {"role": "assistant", "content": "I understood."},
        {
            "role": "user",
            "content": "Based on the prerequisite, please modify only the {NA} in the following content and output it.If no relevant information is found, it's fine to leave it as NA."
            + "Please delete the 'sourse' column. Please make sure to delete the 'Source' column. It's absolutely necessary. Can you convert this into a dictionary type with 'Name' as the key and 'Value' as the value?"
            + specifics_string,
        },
        # {
        #     "role": "assistant",
        #     "content": "Sure. What information should I base this on?",
        # },
        # {
        #     "role": "user",
        #     "content": item_title + " " + gpt_img_description,
        # },
    ],
    max_tokens=600,
)

# 応答オブジェクトから 'content' を抽出
gpt_speifics = response_specifics.choices[0].message.content

print("GPTスペシフィック", gpt_speifics)

import re

# 例として与えられた全体のテキスト
gpt_specifics_data = f"""
{gpt_speifics}
"""

# 辞書の開始と終了を見つける
match = re.search(r"\{.*?\}", gpt_specifics_data, re.DOTALL)

if match:
    dict_text = match.group(0)
    # 辞書として解釈
    specifics_dictionary = eval(dict_text)
    print("データ整形後", specifics_dictionary)
else:
    print("辞書型のデータが見つかりませんでした。")

import pandas as pd

# specifics_dictionaryを使用してデータフレームを作成
df = pd.DataFrame([specifics_dictionary])

# ヘッダー行（列名）の各セルに"C:"を追加
df.columns = ["C:" + col for col in df.columns]

# 新しい列 'C:Action' と 'C:Item ID' を追加し、それぞれの値を設定
df["Action"] = "Revise"
df["Item ID"] = item_id  # ここで 'item_id' は上記で指定した変数です

# 新しい列を先頭に移動
df = df[
    ["Action", "Item ID"] + [col for col in df if col not in ["C:Action", "C:Item ID"]]
]

# データフレームをCSVファイルとして出力
df.to_csv("item_specifics.csv", index=False)

# # Datastoreに保存
# from google.cloud import datastore

# client = datastore.Client()  # Google Cloud Datastoreクライアントの初期化
# SELECTED_ITEMS_KEY = "selected_items"  # 一括更新される商品IDを保存するキー

# key = client.key("EbayItem", item_id)
# entity = client.get(key) or datastore.Entity(key=key)  # エンティティを取得（存在しない場合は新規作成）
# entity["gpt_dspecifics"] = specifics_dictionary  # エンティティに画像説明を追加
# entity.update(specifics_dictionary)
# client.put(entity)
# print("Datastoreに保存しました。")
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

# import openai
# import os
# from openai import OpenAI

# client = OpenAI()
