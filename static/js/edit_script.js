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
