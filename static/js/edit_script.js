$(document).ready(function() {
    // リアルタイムプレビュー機能
    $('#editTitle').on('input', function() {
        $('#previewTitle').text($(this).val());
    });
    $('#editDescription').on('input', function() {
        $('#previewDescription').text($(this).val());
    });
    $('#editPrice').on('input', function() {
        $('#previewPrice').text('$' + $(this).val());
    });
    $('#editImage').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('#previewImage').attr('src', e.target.result);
            };
            reader.readAsDataURL(file);
        }
    });

    // 保存ボタンの処理
    $('#saveChanges').click(function() {
        // Ajaxを使用して変更を保存する処理を記述する
        // ...
    });
});

$(document).ready(function() {
    $('.auto-resize').each(function() {
        this.style.height = (this.scrollHeight) + 'px';
    }).on('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

$(document).ready(function() {
    var $editTitle = $('#editTitle');
    var $titleCount = $('#titleCount');

    // 初期ロード時の文字数を設定
    updateTitleCount();

    $editTitle.on('input', function() {
        updateTitleCount();
        // auto-resizeロジック
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    function updateTitleCount() {
        var currentLength = $editTitle.val().length;
        $titleCount.text(currentLength + ' / 80');
    }
});


let itemId; // グローバルスコープでitemIdを保持

document.addEventListener('DOMContentLoaded', function() {
    // URLのパス部分をスラッシュで分割
    const pathSegments = window.location.pathname.split('/');

    // パスの最後の部分を itemId として取得
    itemId = pathSegments[pathSegments.length - 1];
    console.log('Editing item with ID:', itemId);

    // ここで itemId を使用して処理を行う
});


// 背景削除ボタンのクリックイベント
document.getElementById('removeBackgroundButton').addEventListener('click', function(e) {
    e.preventDefault();

    const currentImageUrl = document.getElementById('currentImageUrl').value;

    fetch('/remove-background', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageUrl: currentImageUrl, itemId: itemId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            // 新しい画像でプレビューを更新
            document.getElementById('previewImage').src = data.newImageUrl;
        } else {
            alert("Failed to remove background.");
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});


// 背景削除およびeBayへのアップロードボタンのイベントリスナー
document.getElementById('removeBackgroundAndUploadToEbayButton').addEventListener('click', function(e) {
    e.preventDefault();

    const imageUrl = document.getElementById('previewImage').src;

    fetch('/remove-background-and-upload-to-ebay', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ imageUrl: imageUrl, itemId: itemId }) // itemIdも送信する
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('Background removed and eBay listing updated successfully.');
        } else {
            alert('Failed to remove background or update eBay listing.');
        }
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

document.getElementById("updateEbayListingButton").addEventListener("click", function() {

    fetch("/update_ebay_img_listing", {
        method: "POST",
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ itemId: itemId })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("eBay listing updated successfully!");
        } else {
            alert("Failed to update eBay listing.");
        }
    })
    .catch((error) => {
        console.error('Error:', error);
        alert("An error occurred while updating eBay listing.");
    });
});

$(document).ready(function() {
    $.ajax({
        url: '/image-list',
        type: 'GET',
        success: function(images) {
            var imageList = $('#imageList');
            images.forEach(function(image) {
                var imageElement = $('<div>', {class: 'image-item'});
                imageElement.append($('<img>', {src: image.url, alt: image.name}));
                imageElement.append($('<button>', {
                    class: 'select-image',
                    text: 'Select',
                    'data-url': image.url
                }));
                imageList.append(imageElement);
            });
        },
        error: function(error) {
            console.log(error);
        }
    });
});


$(document).ready(function() {
    $('#image-selection-form').on('submit', function(e) {
        e.preventDefault();
        var selectedImageUrl = $('input[name="selectedImage"]:checked').val();
        if (selectedImageUrl) {
            $.ajax({
                url: '/your-server-endpoint', // 画像の URL を送信するサーバーサイドのエンドポイント
                type: 'POST',
                data: { imageUrl: selectedImageUrl },
                success: function(response) {
                    // 成功時の処理
                    alert('Image selected successfully');
                },
                error: function(error) {
                    // エラー処理
                    alert('Error selecting image');
                }
            });
        } else {
            alert('Please select an image');
        }
    });
});

