/**
 * Revert the username input field back to the default state, as if the user
 * hasn't entered anyting.
 */
var default_username_state = function(form_group) {
    form_group.removeClass('has-error');
    form_group.removeClass('has-success');
    form_group.find('#status-check span').hide();
    form_group.find('.errorlist').hide();
    form_group.find('#status-check span#default').show();
}
var show_username_local_error = function(form_group, error) {
    form_group.addClass('has-error');
    form_group.removeClass('has-success');

    form_group.find('#status-check span').hide();
    form_group.find('#status-check span#default').show();
};
var show_username_available = function(form_group) {
    form_group.removeClass('has-error');
    form_group.addClass('has-success');
    form_group.find('.errorlist').hide();
    form_group.find('#status-check span').hide();
    form_group.find('#status-check span#username-available').show();
}
var show_username_not_available = function(form_group) {
    form_group.addClass('has-error');
    form_group.removeClass('has-success');
    form_group.find('.errorlist').hide();
    form_group.find('#status-check span').hide();
    form_group.find('#status-check span#username-not-available').show();
}

var check_username = function(form_group) {
    var val = form_group.find('input#id_username_0').val();

    if (val.length < MIN_USERNAME_LENGTH) {
        default_username_state(form_group);
        return;
    } else if (/[@\s]/.test(val) || val.length > MAX_USERNAME_LENGTH) {
        show_username_local_error(form_group);
        return;
    }

    var username = form_group.find('input#id_username_0').val();
    var domain = form_group.find('select#id_username_1 option:selected').val();

    var exists_url = $('meta[name="xmpp-accounts:api-user-available"]').attr('content');

    $.post(exists_url, {
        username: username,
        domain: domain
    }).done(function(data) { // user exists!
        show_username_available(form_group);
    }).fail(function(data) {
        show_username_not_available(form_group);
    });
};

$(document).ready(function() {
    jQuery('#id_username_0').on('input propertychange paste', function(e) {
        var form_group = $(e.target).parent('.form-group');
        check_username(form_group);
    });
    $('#id_username_1').change(function(e) {
        var form_group = $(e.target).parent('.form-group');
        check_username(form_group);
    });
});
