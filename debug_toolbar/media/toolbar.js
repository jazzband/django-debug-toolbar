jQuery.noConflict();
jQuery(function($j) {
	var COOKIE_NAME = 'dj_debug_panel';
	$j.djDebug = function(data, klass) {
		$j.djDebug.init();
	}
	$j.extend($j.djDebug, {
		init: function() {
			var current = null;
			$j('#djDebugPanelList li a').click(function() {
				if (!this.className) {
					return false;
				}
				current = $j('#djDebug #' + this.className);
				if (current.is(':visible')) {
					$j(document).trigger('close.djDebug');
				} else {
					$j('.panelContent').hide();
					current.show();
					$j.djDebug.open();
				}
				return false;
			});
			$j('#djDebug a.close').click(function() {
				$j(document).trigger('close.djDebug');
				return false;
			});
			$j('#djDebug a.remoteCall').click(function() {
				$j('#djDebugWindow').load(this.href, {}, function() {
					$j('#djDebugWindow a.back').click(function() {
						$j(this).parent().hide();
						return false;
					});
				});
				$j('#djDebugWindow').show();
				return false;
			});
			$j('#djDebugTemplatePanel a.djTemplateShowContext').click(function() {
				$j.djDebug.toggle_content($j(this).parent().next());
				return false;
			});
			$j('#djDebugSQLPanel a.djSQLShowStacktrace').click(function() {
				$j.djDebug.toggle_content($j(this).parent().next());
				return false;
			});
			$j('#djHideToolBarButton').click(function() {
				$j.djDebug.hide_toolbar(true);
				return false;
			});
			$j('#djShowToolBarButton').click(function() {
				$j.djDebug.show_toolbar();
				return false;
			});
			if ($j.cookie(COOKIE_NAME)) {
				$j.djDebug.hide_toolbar(false);
			} else {
				$j('#djDebugToolbar').show();
			}
		},
		open: function() {
			$j(document).bind('keydown.djDebug', function(e) {
				if (e.keyCode == 27) {
					$j.djDebug.close();
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
			$j(document).trigger('close.djDebug');
			return false;
		},
		hide_toolbar: function(setCookie) {
			$j('#djDebugToolbar').hide("fast");
			$j(document).trigger('close.djDebug');
			$j('#djDebugToolbarHandle').show();
			if (setCookie) {
				$j.cookie(COOKIE_NAME, 'hide', {
					path: '/',
					expires: 10
				});
			}
		},
		show_toolbar: function() {
			$j('#djDebugToolbarHandle').hide();
			$j('#djDebugToolbar').show("fast");
			$j.cookie(COOKIE_NAME, null, {
				path: '/',
				expires: -1
			});
		}
	});
	$j(document).bind('close.djDebug', function() {
		$j(document).unbind('keydown.djDebug');
		$j('.panelContent').hide();
	});
});
jQuery(function() {
	jQuery.djDebug();
});
