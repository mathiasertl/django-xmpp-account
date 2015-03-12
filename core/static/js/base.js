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

    if (val.length < MIN_USERNAME_LENGTH) {
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

var exists_timeout;
var username_exists_check = function() {
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
            form_group.removeClass('has-error');
            statuscheck.find('span').hide();
            if (data.status == 404) {
                statuscheck.find('#username-ok').show();
            } else {
                statuscheck.find('#username-error').show();
            }
        });
    }, 500);
}

$(document).ready(function() {
    $('#id_username').keypress(function(data) {
        if (data.which == 0) {  // 0 == tab
            return;
        }
        if (basic_username_check()) {
            username_exists_check();
        }
    });

    $('#id_email').keypress(function() {
        if (data.which == 0) {  // 0 == tab
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

    $('.fblike').on('click', function(event) {
        // Generate a string containing the HTML to place in the element (for readability)
        var html = "<div id=\"fb-root\">\n";
        html += "<div class=\"fb-follow\" data-href=\"https://www.facebook.com/" + FACEBOOK_PAGE + "\" data-colorscheme=\"light\" data-layout=\"button\" data-show-faces=\"true\"></div>\n";
        html += "<div class=\"fb-like\" data-href=\"https://facebook.com/" + FACEBOOK_PAGE + "\" data-send=\"true\" data-layout=\"button_count\" data-width=\"100\" data-show-faces=\"false\" data-font=\"arial\">\n";
        html += "</div>\n";

        // Replace the specified element's contents with the HTML necessary to display the
        // Like/+1 Buttons, *before* loading the SDKs below
        $('.fblike').html(html);

        // This is the code provided by facebook to asynchronously load their SDK
        var e = document.createElement('script'); e.async = true;
        e.src = document.location.protocol +
          '//connect.facebook.net/en_US/all.js#xfbml=1';
        document.getElementById('fb-root').appendChild(e);
    });

    $('.twitter-follow').on('click', function(event) {
        var html = '<iframe src="//platform.twitter.com/widgets/follow_button.html?screen_name=' + TWITTER_PAGE + '&show_count=false&dnt=true" style="width: 300px; height: 20px;" allowtransparency="true" frameborder="0" scrolling="no"></iframe>';
        $('.twitter-follow').html(html);
    });
});
