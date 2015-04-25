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

var basic_username_check = function() {
    var val = $('input#id_username').val();
    var form_group = $('div#fg_username');
    var status_check = $('#status-check')

    if (val.length == 0) {
        status_check.find('span').hide();
        status_check.find('#default').show();
        form_group.removeClass('has-error');
        return false;
    } else if (val.length < MIN_USERNAME_LENGTH) {
        status_check.find('span').hide();
        status_check.find('#default').show();
        form_group.addClass('has-error');
        return false;
    } else if (/[@\s]/.test(val) || val.length > MAX_USERNAME_LENGTH) {
        status_check.find('span').hide();
        status_check.find('#username-error').show();
        form_group.addClass('has-error');
        return false;
    }
    return true;
}

var ignored_keys = [0, 16, 17, 18, 20, 27, 33, 34, 35, 36, 45, 91, 144];
var exists_timeout;
var username_exists_check = function() {
    if ($('body.register').length == 0) {
        return;  // only check username on registration page
    }
    if (typeof exists_timeout !== "undefined") {
        clearTimeout(exists_timeout)
    }
    var statuscheck = $('#status-check')
    statuscheck.find('span[id!="checking"]').hide();
    statuscheck.find('span#checking').show();

    /** we use a timeout so that fast-typing users don't cause to many requests */
    exists_timeout = setTimeout(function() {
        if (! basic_username_check()) {
            return;
        }
        var form_group = $('.form-group#fg_username');
        var username = $('input#id_username').val();
        var domain = $('select#id_domain option:selected').val();

        $.post(exists_url, {
            username: username,
            domain: domain
        }).done(function(data) { // user exists!
            form_group.addClass('has-error');
            statuscheck.find('span').hide();
            statuscheck.find('#username-taken').show();
        }).fail(function(data) { 
            statuscheck.find('span').hide();
            if (data.status == 404) {
                statuscheck.find('#username-ok').show();
                form_group.removeClass('has-error');
            } else {
                statuscheck.find('#username-error').show();
                form_group.addClass('has-error');
            }
        });
    }, 500);
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
    console.log('load_facebook()');
    if (! fb_loaded) {
        console.log("Load Facebook SDK");
        var e = document.createElement('script'); e.async = true;
        e.src = document.location.protocol +
          '//connect.facebook.net/en_US/all.js#xfbml=1';
        document.getElementById('fb-root').appendChild(e);
    }
    fb_loaded = true;
};


$(document).ready(function() {
    show_fingerprint_msg();

    $('#id_username').keyup(function(data) {
        if (ignored_keys.indexOf(data.which) !== -1) { 
            return;
        }
        if (basic_username_check()) {
            username_exists_check();
        }
    });
    $('#id_domain').change(function() {
        show_fingerprint_msg();
        if (basic_username_check()) {
            username_exists_check();
        }
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
        link = $(event.target);
        url = link.attr('href');
        width = link.attr('data-width');
        height = link.attr('data-height');
        window.open(url, 'newwindow', 'width=' + width + ', height=' + height);
        return false;
    });
    $('#myModal').on('show.bs.modal', function(e) {
        console.log('show.bs.modal!');
        load_facebook();
    });
});
