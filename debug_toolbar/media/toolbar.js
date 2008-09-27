var _$ = window.$;
jQuery.noConflict();
jQuery(function($) {
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
