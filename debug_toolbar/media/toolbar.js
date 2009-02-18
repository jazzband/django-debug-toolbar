var _$ = window.$;
$j = jQuery.noConflict();
jQuery(function() {
	var COOKIE_NAME = 'dj_debug_panel';
	$j.djDebug = function(data, klass) {
		$j.djDebug.init();
	}
	$j.extend($j.djDebug, {
		init: function() {
			var current = null;
			$j('#djDebugPanelList li a').click(function() {
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
			});
			$j('#djHideToolBarButton').click(function() {
				$j.djDebug.hide_toolbar(true);
			});
			$j('#djShowToolBarButton').click(function() {
				$j.djDebug.show_toolbar();
			});
			if ($j.cookie(COOKIE_NAME)) {
				$j.djDebug.hide_toolbar(false);
			} else {
				$j('#djDebugToolbar').show();
			}
			$j(window).load($j.djDebug.format_panels);
			$j(window).resize($j.djDebug.format_panels);
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
		},
		/* Make sure that panel layout doesn't overflow the screen
		 * width. Any panel that would otherwise wrap to the next line
		 * are pushed into a "more..." vertical display in the final
		 * panel position. */
		format_panels: function () {
			// If we've already done some overflow-avoidance, undo the
			// effect before recomputing (needed, for example, after a
			// window resize).
			$j("#djDebugMore > ul > li").appendTo("#djDebugPanelList");
			$j("#djDebugMore").remove();

			// Check for wrapping by examing the position of the last
			// element.
			var row_top = $j("#djDebugPanelList > li").position().top;
			var final_pos = $j("#djDebugPanelList > li:last").position();

			if (final_pos.top == row_top && final_pos.left != 0) {
				return;
			}

			function overflow_check(idx) {
				pos = $j(this).position();
				return pos.top > row_top || (idx > 1 && pos.left == 0);
			};

			var more = $j("<li id='djDebugMore'>More...<ul></ul></li>");
			more.prependTo("#djDebugPanelList");
			overflows = $j("#djDebugPanelList > li").filter(overflow_check);
			more.appendTo("#djDebugPanelList");
			$j("#djDebugMore > ul").append(overflows);
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

$ = _$;

