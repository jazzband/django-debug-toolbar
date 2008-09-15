jQuery.noConflict();
jQuery(document).ready(function() {
    var current = null;
    jQuery('#djDebugPanelList li a').click(function() {
        if (current) { current.hide(); }
        current = jQuery('#djDebug #' + this.className);
        current.show();
        return false;
    });
    jQuery('#djDebug a.close').click(function() {
        if (current) { current.hide(); }
        current = null;
        return false;
    })
});
