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