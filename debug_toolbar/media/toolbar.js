var _$ = window.$;
jQuery.noConflict();
jQuery(function($) {
	var COOKIE_NAME = 'dj_debug_panel';
	$.djDebug = function(data, klass) {
		$.djDebug.init();
	}
	$.extend($.djDebug, {
		init: function() {
			var current = null;
			$('#djDebugPanelList li a').click(function() {
				current = $('#djDebug #' + this.className);
				if (current.is(':visible')) {
					$(document).trigger('close.djDebug');
				} else {
					$('.panelContent').hide();
					current.show();
					$.djDebug.open();
				}
				return false;
			});
			$('#djDebug a.close').click(function() {
				$(document).trigger('close.djDebug');
				return false;
			});
			$('#djDebug a.remoteCall').click(function() {
				$('#djDebugWindow').load(this.href, {}, function() {
					$('#djDebugWindow a.back').click(function() {
						$(this).parent().hide();
						return false;
					});
				});
				$('#djDebugWindow').show();
				return false;
			});
			$('#djDebugTemplatePanel a.djTemplateShowContext').click(function() {
				$.djDebug.toggle_content($(this).parent().next());
			});
			$('#djHideToolBarButton').click(function() {
				$.djDebug.hide_toolbar(true);
			});
			$('#djShowToolBarButton').click(function() {
				$.djDebug.show_toolbar();
			});
			if ($.cookie(COOKIE_NAME)) {
				$.djDebug.hide_toolbar(false);
			} else {
				$('#djDebugToolbar').show();
			}
		},
		open: function() {
			$(document).bind('keydown.djDebug', function(e) {
				if (e.keyCode == 27) {
					$.djDebug.close();
				}
			});
		},
		toggle_content: function(elem) {
			if (elem.is(':visible')) {
				elem.hide();
			} else {
				elem.show();
			}
		},
		close: function() {
			$(document).trigger('close.djDebug');
			return false;
		},
		hide_toolbar: function(setCookie) {
			$('#djDebugToolbar').hide("fast");
			$('#djDebugToolbarHandle').show();
			if (setCookie) {
				$.cookie(COOKIE_NAME, 'hide', {
					path: '/',
					expires: 10
				});
			}
		},
		show_toolbar: function() {
			$('#djDebugToolbarHandle').hide();
			$('#djDebugToolbar').show("fast");
			$.cookie(COOKIE_NAME, null, {
				path: '/',
				expires: -1
			});
		}
	});
	$(document).bind('close.djDebug', function() {
		$(document).unbind('keydown.djDebug');
		$('.panelContent').hide();
	});
});
jQuery(function() {
	jQuery.djDebug();
});
$ = _$;

