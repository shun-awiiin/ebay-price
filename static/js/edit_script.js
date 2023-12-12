$(document).ready(function() {
    $('#editTitle, #editDescription, #editPrice').on('input', function() {
        var previewId = '#preview' + this.id.substring(4);
        $(previewId).text($(this).val());
    });

    $('#editImage').on('change', function() {
        var file = this.files[0];
        if (file) {
            var reader = new FileReader();
            reader.onload = function(e) {
                $('#previewImage').attr('src', e.target.result).show();
            };
            reader.readAsDataURL(file);
        } else {
            $('#previewImage').hide();
        }
    });
});
