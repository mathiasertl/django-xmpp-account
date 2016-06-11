function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

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

var show_fingerprint_msg = function() {
    var id = 'fp-' + $('#id_domain option:selected').val();
    $('.fingerprint[id!="' + id + '"]').hide();
    $('.fingerprint[id="' + id + '"]').show();
};

/**
 * Code to insert Facebook SDK.
 */
var fb_loaded = false;
var load_facebook = function() {
    // This is the code provided by facebook to asynchronously load their SDK
    if (! fb_loaded) {
        var e = document.createElement('script'); e.async = true;
        e.src = document.location.protocol +
          '//connect.facebook.net/en_US/all.js#xfbml=1';
        document.getElementById('fb-root').appendChild(e);
    }
    fb_loaded = true;
};


$(document).ready(function() {
    show_fingerprint_msg();

    jQuery('#id_username_0').on('input propertychange paste', function(e) {
        var form_group = $(e.target).parent('.form-group');
        check_username(form_group);
    });
    $('#id_username_1').change(function(e) {
        show_fingerprint_msg();
        var form_group = $(e.target).parent('.form-group');
        check_username(form_group);
    });

    $('.gpg-fields-toggle').click(function(data) {
        $('.gpg-fields-toggle .show-triangle').toggle();
        $('.gpg-fields-toggle .hide-triangle').toggle();
        $('.gpg-form-group .row').slideToggle();
    });

    $('#id_email').keyup(function(data) {
        if (ignored_keys.indexOf(data.which) !== -1) {
            return;
        }
        var re = /^(([^<>()[\]\\.,;:\s@\"]+(\.[^<>()[\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        var input = $(this);
        var form_group = input.parents('div.form-group');
        if (re.test($(this).val())) {
            form_group.removeClass('has-error');
        } else {
            form_group.addClass('has-error');
        }
    });

    $('a.social').on('click', function(event) {
        link = $(event.currentTarget);
        url = link.attr('href');
        width = link.attr('data-width');
        height = link.attr('data-height');
        window.open(url, 'newwindow', 'width=' + width + ', height=' + height);
        return false;
    });

    /* This is only displayed on the submit page of a registration confirmation. */
    $('#fb-page-modal').on('show.bs.modal', function(e) {
        load_facebook();
    });

    $('.js-captcha-refresh').click(function(){
        $form = $(this).parents('form');

        $.getJSON(captcha_refresh_url, {}, function(json) {
            // This should update your captcha image src and captcha hidden input
            $('#captcha-form-data img').attr('src', json.image_url);
            $('#captcha-form-data input[type="hidden"]').attr('value', json.key);
        });

        return false;
    });
});
