(function (factory) {
    if (typeof define === 'function' && define.amd && typeof require === 'function') {
        // RequireJS, use jQuery from its config
        require(['jquery'], factory);
    } else {
        factory(jQuery);
    }
}(function ($) {
    $('#djDebug a.djDebugToggle').on('click', function(e) {
        e.preventDefault();
        $(this).parent().find('.djDebugCollapsed').toggle();
        $(this).parent().find('.djDebugUncollapsed').toggle();
    });
}));
