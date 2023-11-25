# 必要なライブラリと設定をインポート
from ebaysdk.trading import Connection as Trading

# API接続の設定
api = Trading(
    domain="api.ebay.com",
    config_file=None,
    appid="shunkiku-tooltest-PRD-690cb6562-fcc8791f",
    devid="8480f8f3-218c-48ff-bd22-0a6787809783",
    certid="PRD-ac3fefa98a56-06a1-4e54-9fbd-fd7b",
    token="v^1.1#i^1#I^3#p^3#f^0#r^0#t^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",
    siteid="0",
)

# 商品IDを設定
item_id = "364540394327"

# APIリクエストの作成
request = {"ItemID": item_id, "DetailLevel": "ReturnAll", "IncludeItemSpecifics": True}
# APIコールを実行して応答を取得
get_item_specifics_response = api.execute("GetItem", request)
# 応答を辞書形式で取得
response_dict = get_item_specifics_response.dict()
# 応答からItemSpecificsのみを抽出
item_specifics = (
    response_dict.get("Item", {}).get("ItemSpecifics", {}).get("NameValueList", [])
)
item_description = response_dict.get("Item", {}).get("Description", "")

print("アイテム詳細", item_specifics)
print("商品説明", item_description)
