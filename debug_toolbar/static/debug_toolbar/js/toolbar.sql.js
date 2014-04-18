(function (factory) {
    if (typeof define === 'function' && define.amd) {
        if (typeof require === 'function') {
          // RequireJS, use jQuery from its config
          require(['jquery'], factory);
        } else {
          // AMD, but not RequireJS. Register as anonymous module.
          define(['jquery'], factory);
        }
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
