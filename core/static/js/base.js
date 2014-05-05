$(document).ready(function() {
    $('label[for="id_value"]').parent().hide();

    $('#id_username').keyup(function() {
        var input = $(this);
        var form_group = input.parents('div.form-group');
        if (/[@\s]/.test($(this).val())) {
            form_group.addClass('has-error');
        } else {
            form_group.removeClass('has-error');
        }
    });
});
