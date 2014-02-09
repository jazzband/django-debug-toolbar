(function (factory) {
    if (typeof define === 'function' && define.amd) {
        define(['djdt.jquery'], factory);
    } else {
        factory(djdtjQuery);
    }
}(function ($) {
    $('#djDebug a.djDebugToggle').on('click', function(e) {
        e.preventDefault();
        $(this).parent().find('.djDebugCollapsed').toggle();
        $(this).parent().find('.djDebugUncollapsed').toggle();
    });
}));
