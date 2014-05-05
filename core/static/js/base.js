$(document).ready(function() {
    $('label[for="id_value"]').parent().hide();

    $('#id_username').keyup(function() {
        var input = $(this);
        var form_group = input.parents('div.form-group');
        var val = $(this).val();

        if (/[@\s]/.test(val) || val.length < MIN_USERNAME_LENGTH || val.length > MAX_USERNAME_LENGTH) {
            form_group.addClass('has-error');
        } else {
            form_group.removeClass('has-error');
        }
    });

    $('#id_email').keyup(function() {
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        var input = $(this);
        var form_group = input.parents('div.form-group');
        if (re.test($(this).val())) {
            form_group.removeClass('has-error');
        } else {
            form_group.addClass('has-error');
        }
    });
});
