$(document).ready(function() {
    $('#id_email').on('input propertychange paste', function(data) {
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;

        var input = $(this);
        var value = input.val();
        var form_group = input.parents('div.form-group');

        if (! value) {
            form_group.removeClass('has-error');
            form_group.removeClass('has-success');
        } else if (re.test(value)) {
            form_group.removeClass('has-error');
            form_group.addClass('has-success');
        } else {
            form_group.addClass('has-error');
            form_group.removeClass('has-success');
        }
    });
});
