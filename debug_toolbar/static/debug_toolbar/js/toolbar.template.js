(function (factory) {
    if (typeof define === 'function' && define.amd && typeof require === 'function') {
        // RequireJS, use jQuery from its config
        require(['jquery'], factory);
    } else {
        factory(jQuery);
    }
}(function ($) {
    var uarr = String.fromCharCode(0x25b6),
        darr = String.fromCharCode(0x25bc);

    $('a.djTemplateShowContext').on('click', function() {
        var arrow = $(this).children('.toggleArrow');
        arrow.html(arrow.html() == uarr ? darr : uarr);
        $(this).parent().next().toggle();
        return false;
    });
}));
