// openModal関数の定義
function openModal(button) {
var itemId = button.getAttribute('data-item-id');
var currentPrice = button.getAttribute('data-current-price');

// モーダルウィンドウの要素に値をセット
$('#modalItemId').val(itemId);
$('#newPrice').val(currentPrice);

// モーダルウィンドウを表示
$('#priceUpdateModal').modal('show');
}

// Ajaxリクエストの定義
// 価格更新フォームの送信処理
$('#priceUpdateForm').submit(function(e) {
    e.preventDefault();
    var formData = $(this).serialize();

    $.ajax({
        url: '/revise-price',
        type: 'POST',
        data: formData,
        success: function(response) {
            if (response.status === "success") {
                // モーダルを閉じてリストを更新
                $('#priceUpdateModal').modal('hide');
                updateListing(response.itemId, response.newPrice);
            } else {
                alert(response.message);
            }
        },
    });
});
function updateListing(itemId, newPrice) {
    $(".card").each(function() {
        var itemCard = $(this);
        if (itemCard.find('.btn-primary').data("item_id") === itemId) {
            itemCard.find(".card-text").text("$ " + newPrice);
        }
    });
}
    
$('#bulk-decrease-price-form').submit(function(e) {
    e.preventDefault();
    var selectedItems = $('.form-check-input:checked').map(function() {
        return this.value;
    }).get();
    console.log(selectedItems); 

    var decreaseAmount = $('#decrease-amount-input').val(); // ユーザーが入力した値を取得

    // 選択された商品IDと新しい価格をサーバーに送信
    $.ajax({
        url: '/bulk-decrease-price',
        type: 'POST',
        data: {
            item_ids: selectedItems,
            decrease_amount: decreaseAmount // ユーザーが指定した値を使用
        },
        success: function(response) {
            alert('Selected items prices were decreased successfully.');
            // 必要に応じてフロントエンドを更新
        },
        error: function(error) {
            alert('Error decreasing prices of selected items.');
        }
    });
});

// HTMLエスケープ処理を行う関数
function escapeHtml(unsafeText) {
    return unsafeText
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function startTutorial() {
    introJs().start();
}
