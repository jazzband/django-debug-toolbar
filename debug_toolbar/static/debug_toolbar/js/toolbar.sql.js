(function (factory) {
    if (typeof define === 'function' && define.amd) {
        define('django-debug-sql', ['jquery'], factory);
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
