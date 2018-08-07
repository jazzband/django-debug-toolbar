(function ($) {
    $('#djDebug a.djDebugToggle').on('click', function(event) {
        event.preventDefault();
        $(this).parent().find('.djDebugCollapsed').toggle();
        $(this).parent().find('.djDebugUncollapsed').toggle();
    });
    djdt.applyStyle('background-color');
    djdt.applyStyle('left');
    djdt.applyStyle('width');
})(djdt.jQuery);
