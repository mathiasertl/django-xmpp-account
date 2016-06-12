var show_fingerprint_msg = function() {
    var id = 'fp-' + $('#id_username_1 option:selected').val();
    $('.fingerprint[id!="' + id + '"]').hide();
    $('.fingerprint[id="' + id + '"]').show();
};

$(document).ready(function() {
    show_fingerprint_msg();
    $('#id_username_1').change(function(e) {
        show_fingerprint_msg();
    });

    $('.gpg-fields-toggle').click(function(data) {
        $('.gpg-fields-toggle .show-triangle').toggle();
        $('.gpg-fields-toggle .hide-triangle').toggle();
        $('.gpg-form-group .row').slideToggle();
    });
});
