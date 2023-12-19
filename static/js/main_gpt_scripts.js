$(".generate-title-btn").click(function() {
    var itemId = $(this).data("item-id");
    var GPTdescription = $(this).data("description");

    // GPTdescriptionが空の場合の処理
    if (!GPTdescription) {
        alert("Description is empty. Cannot generate title.");
        return; // 以降の処理を中断
    }

    $.ajax({
        url: '/generate-gpt-title',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({item_id : itemId , gpt_description: GPTdescription }),
        success: function(response) {
            if (response.status === "success") {
                // 成功した場合の処理
                alert("Generated Title: " + response.generated_title);
            } else {
                alert("Failed to generate title: " + response.message);
            }
        },
        error: function(error) {
            alert("An error occurred while generating the title.");
        }
    });
});

$(".gpt-item-description-btn").click(function() {
var itemId = $(this).data("item-id");
var imageUrl = $(this).data("image-url");

if (!imageUrl) {
    alert("No image available for description generation.");
    return;
}

    // GPTを使用して説明文を生成し、データベースに保存するリクエスト
    $.ajax({
        url: '/gpt-item-description',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ item_id: itemId, image_url: imageUrl }),
        success: function(response) {
            if (response.status === "success") {
                // 説明文を表示する
                $(".gpt-description-text").text(response.gpt_description).show();
            } else {
                alert("Failed to generate and save description: " + response.message);
            }
        },
        error: function(error) {
            alert("An error occurred while generating and saving the description.");
        }
    });
});

 // タイトル更新フォームの送信処理
 $(document).ready(function() {
    $(".update-title-btn").click(function() {
        var itemId = $(this).data("item-id");
        var newTitle = $(this).data("generated-title");

        // Ajaxリクエストを送信
        $.ajax({
            url: '/revise-title',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ item_id: itemId, new_title: newTitle }),
            success: function(response) {
                if (response.status === "success") {
                    alert("Title updated successfully.");
                    // ここでフロントエンドの表示を更新する処理を追加
                } else {
                    alert("Failed to update title: " + response.message);
                }
            },
            error: function(error) {
                alert("An error occurred while updating the title.");
            }
        });
    });
});


$(document).on('click', '.edit-item-btn', function() {
    var itemId = $(this).data('item-id');
    // 編集ページにアイテムIDを渡す方法を実装
    // 例: クエリパラメータとして渡す
    window.location.href = '/edit-item/' + itemId;
});

document.getElementById('listingsArea').addEventListener('submit', function(event) {
    if (event.target.matches('.revise-description-form')) {
        event.preventDefault();

        var formData = new FormData(event.target);
        var data = {
            item_id: formData.get('item_id'),
            new_description: formData.get('new_description')
        };

        fetch('/revise-item-description', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            var resultMessageDiv = event.target.nextElementSibling;
            if (data.success) {
                // 成功時のメッセージを表示
                resultMessageDiv.textContent = 'Success: ' + data.message;
                resultMessageDiv.style.color = 'green'; // 成功メッセージの色を緑に設定
            } else {
                // エラー時のメッセージを表示
                resultMessageDiv.textContent = 'Error: ' + data.message;
                resultMessageDiv.style.color = 'red'; // エラーメッセージの色を赤に設定
            }
        })
        .catch((error) => {
            // ネットワークエラーやその他のエラーの処理
            var resultMessageDiv = event.target.nextElementSibling;
            resultMessageDiv.textContent = 'An error occurred: ' + error.message;
            resultMessageDiv.style.color = 'red'; // エラーメッセージの色を赤に設定
        });
    }
});

document.addEventListener('DOMContentLoaded', function() {
    // "revise-specifics-gpt-btn"クラスを持つボタンにイベントリスナーを設定
    const buttons = document.querySelectorAll('.revise-specifics-gpt-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            const itemId = this.getAttribute('data-item-id');
            const gptDescription = this.getAttribute('data-gpt-description');
            generateItemSpecificsWithGPT(itemId, gptDescription);
        });
    });
});

function generateItemSpecificsWithGPT(itemId, gptDescription) {
    // Ajaxを使用してサーバーにPOSTリクエストを送信
    fetch('/generate-item-specifics', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            item_id: itemId,
            gpt_description: gptDescription  // GPTで生成された商品の説明を含める
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            alert('Item specifics generated and saved successfully');
        } else {
            alert('Error: ' + data.message);
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
}
