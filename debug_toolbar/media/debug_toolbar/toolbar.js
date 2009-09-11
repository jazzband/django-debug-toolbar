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
					$j(this).parent().removeClass('active');
				} else {
					$j('.panelContent').hide(); // Hide any that are already open
					current.show();
					$j.djDebug.open();
					$j('#djDebugToolbar li').removeClass('active');
					$j(this).parent().addClass('active');
				}
				return false;
			});
			$j('#djDebug a.close').click(function() {
				$j(document).trigger('close.djDebug');
				$j('#djDebugToolbar li').removeClass('active');
				return false;
			});
			$j('#djDebug a.remoteCall').click(function() {
				$j('#djDebugWindow').load(this.href, {}, function() {
					$j('#djDebugWindow a.back').click(function() {
						$j(this).parent().parent().hide();
						return false;
					});
				});
				$j('#djDebugWindow').show();
				return false;
			});
			$j('#djDebugTemplatePanel a.djTemplateShowContext').click(function() {
				$j.djDebug.toggle_arrow($j(this).children('.toggleArrow'))
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
				$j.djDebug.show_toolbar(false);
			}
		},
		open: function() {
			// TODO: Decide if we should remove this
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
			// close any sub panels
			$j('#djDebugWindow').hide();
			// close all panels
			$j('.panelContent').hide();
			$j('#djDebugToolbar li').removeClass('active');
			// finally close toolbar
			$j('#djDebugToolbar').hide('fast');
			$j('#djDebugToolbarHandle').show();
			// Unbind keydown
			$j(document).unbind('keydown.djDebug');
			if (setCookie) {
				$j.cookie(COOKIE_NAME, 'hide', {
					path: '/',
					expires: 10
				});
			}
		},
		show_toolbar: function(animate) {
			// Set up keybindings
			$j(document).bind('keydown.djDebug', function(e) {
				if (e.keyCode == 27) {
					$j.djDebug.close();
				}
			});
			$j('#djDebugToolbarHandle').hide();
			if (animate) {
				$j('#djDebugToolbar').show('fast');
			} else {
				$j('#djDebugToolbar').show();
			}
			$j.cookie(COOKIE_NAME, null, {
				path: '/',
				expires: -1
			});
		},
		toggle_arrow: function(elem) {
			var uarr = String.fromCharCode(0x25b6);
			var darr = String.fromCharCode(0x25bc);
			elem.html(elem.html() == uarr ? darr : uarr);
		}
	});
	$j(document).bind('close.djDebug', function() {
		// If a sub-panel is open, close that
		if ($j('#djDebugWindow').is(':visible')) {
			$j('#djDebugWindow').hide();
			return;
		}
		// If a panel is open, close that
		if ($j('.panelContent').is(':visible')) {
			$j('.panelContent').hide();
			return;
		}
		// Otherwise, just minimize the toolbar
		if ($j('#djDebugToolbar').is(':visible')) {
			$j.djDebug.hide_toolbar(true);
			return;
		}
	});
});
jQuery(function() {
	jQuery.djDebug();
});
