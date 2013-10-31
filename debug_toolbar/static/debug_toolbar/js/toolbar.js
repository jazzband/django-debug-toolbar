// Grab jQuery for use in any of the below
var $djdtjq = jQuery.noConflict(true);

window.djdt = (function(window, document, jQuery) {
	jQuery.cookie = function(name, value, options) { if (typeof value != 'undefined') { options = options || {}; if (value === null) { value = ''; options.expires = -1; } var expires = ''; if (options.expires && (typeof options.expires == 'number' || options.expires.toUTCString)) { var date; if (typeof options.expires == 'number') { date = new Date(); date.setTime(date.getTime() + (options.expires * 24 * 60 * 60 * 1000)); } else { date = options.expires; } expires = '; expires=' + date.toUTCString(); } var path = options.path ? '; path=' + (options.path) : ''; var domain = options.domain ? '; domain=' + (options.domain) : ''; var secure = options.secure ? '; secure' : ''; document.cookie = [name, '=', encodeURIComponent(value), expires, path, domain, secure].join(''); } else { var cookieValue = null; if (document.cookie && document.cookie != '') { var cookies = document.cookie.split(';'); for (var i = 0; i < cookies.length; i++) { var cookie = $.trim(cookies[i]); if (cookie.substring(0, name.length + 1) == (name + '=')) { cookieValue = decodeURIComponent(cookie.substring(name.length + 1)); break; } } } return cookieValue; } };
	var $ = jQuery;
	var COOKIE_NAME = 'djdt';
	var djdt = {
		jQuery: jQuery,
		events: {
			ready: []
		},
		isReady: false,
		init: function() {
			$('#djDebug').show();
			var current = null;
			$('#djDebugPanelList li a').live('click', function() {
				if (!this.className) {
					return false;
				}
				current = $('#djDebug #' + this.className);
				if (current.is(':visible')) {
					$(document).trigger('close.djDebug');
					$(this).parent().removeClass('active');
				} else {
					$('.panelContent').hide(); // Hide any that are already open
					current.show();
					$('#djDebugToolbar li').removeClass('active');
					$(this).parent().addClass('active');
				}
				return false;
			});
			$('#djDebug a.djDebugClose').live('click', function() {
				$(document).trigger('close.djDebug');
				$('#djDebugToolbar li').removeClass('active');
				return false;
			});
			$('#djDebug .djDebugPanelButton input[type=checkbox]').live('click', function() {
				$.cookie($(this).attr('data-cookie'), 'off', {
					path: '/',
					expires: $(this).prop('checked') ? -1 : 10
				});
			});

			$('#djDebug .remoteCall').live('click', function() {
				var self = $(this);
				var name = self[0].tagName.toLowerCase();
				var ajax_data = {};

				if (name == 'button') {
					var form = self.parents('form:eq(0)');
					ajax_data['url'] = self.attr('formaction');

					if (form.length) {
						ajax_data['data'] = form.serialize();
						ajax_data['type'] = form.attr('method') || 'POST';
					}
				}

				if (name == 'a') {
					ajax_data['url'] = self.attr('href');
				}

				$.ajax(ajax_data).done(function(data){
					$('#djDebugWindow').html(data).show();
				}).fail(function(xhr){
						var message = '<div class="djDebugPanelTitle"><a class="djDebugClose djDebugBack" href="">Back</a><h3>'+xhr.status+': '+xhr.statusText+'</h3></div>';
						$('#djDebugWindow').html(message).show();
				});

				$('#djDebugWindow a.djDebugBack').live('click', function() {
					$(this).parent().parent().hide();
					return false;
				});

				return false;
			});

			$('#djDebugTemplatePanel a.djTemplateShowContext').live('click', function() {
				djdt.toggle_arrow($(this).children('.toggleArrow'));
				djdt.toggle_content($(this).parent().next());
				return false;
			});
			$('#djDebug a.djDebugToggle').live('click', function(e) {
				e.preventDefault();
				$(this).parent().find('.djDebugCollapsed').toggle();
				$(this).parent().find('.djDebugUncollapsed').toggle();
			});
			$('#djDebug a.djToggleSwitch').live('click', function(e) {
				e.preventDefault();
				var btn = $(this);
				var id = btn.attr('data-toggle-id');
				var open_me = btn.text() == btn.attr('data-toggle-open');
				if (id === '' || !id) {
					return;
				}
				var name = btn.attr('data-toggle-name');
				btn.parents('.djDebugPanelContent').find('#' + name + '_' + id).find('.djDebugCollapsed').toggle(open_me);
				btn.parents('.djDebugPanelContent').find('#' + name + '_' + id).find('.djDebugUncollapsed').toggle(!open_me);
				$(this).parents('.djDebugPanelContent').find('.djToggleDetails_' + id).each(function(){
					var $this = $(this);
					if (open_me) {
						$this.addClass('djSelected');
						$this.removeClass('djUnselected');
						btn.text(btn.attr('data-toggle-close'));
						$this.find('.djToggleSwitch').text(btn.text());
					} else {
						$this.removeClass('djSelected');
						$this.addClass('djUnselected');
						btn.text(btn.attr('data-toggle-open'));
						$this.find('.djToggleSwitch').text(btn.text());
					}
				});
				return;
			});
			function getSubcalls(row) {
				var id = row.attr('id');
				return $('.djDebugProfileRow[id^="'+id+'_"]');
			}
			function getDirectSubcalls(row) {
				var subcalls = getSubcalls(row);
				var depth = parseInt(row.attr('depth'), 10) + 1;
				return subcalls.filter('[depth='+depth+']');
			}
			$('.djDebugProfileRow .djDebugProfileToggle').live('click', function(){
				var row = $(this).closest('.djDebugProfileRow');
				var subcalls = getSubcalls(row);
				if (subcalls.css('display') == 'none') {
					getDirectSubcalls(row).show();
				} else {
					subcalls.hide();
				}
			});
			$('#djHideToolBarButton').click(function() {
				djdt.hide_toolbar(true);
				return false;
			});
			$('#djShowToolBarButton').click(function() {
				djdt.show_toolbar();
				return false;
			});
			$(document).bind('close.djDebug', function() {
				// If a sub-panel is open, close that
				if ($('#djDebugWindow').is(':visible')) {
					$('#djDebugWindow').hide();
					return;
				}
				// If a panel is open, close that
				if ($('.panelContent').is(':visible')) {
					$('.panelContent').hide();
					$('#djDebugToolbar li').removeClass('active');
					return;
				}
				// Otherwise, just minimize the toolbar
				if ($('#djDebugToolbar').is(':visible')) {
					djdt.hide_toolbar(true);
					return;
				}
			});
			if ($.cookie(COOKIE_NAME)) {
				djdt.hide_toolbar(false);
			} else {
				djdt.show_toolbar(false);
			}
			$('#djDebug .djDebugHoverable').hover(function(){
				$(this).addClass('djDebugHover');
			}, function(){
				$(this).removeClass('djDebugHover');
			});
			djdt.isReady = true;
			$.each(djdt.events.ready, function(_, callback){
				callback(djdt);
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
			// close any sub panels
			$('#djDebugWindow').hide();
			// close all panels
			$('.panelContent').hide();
			$('#djDebugToolbar li').removeClass('active');
			// finally close toolbar
			$('#djDebugToolbar').hide('fast');
			$('#djDebugToolbarHandle').show();
			// Unbind keydown
			$(document).unbind('keydown.djDebug');
			if (setCookie) {
				$.cookie(COOKIE_NAME, 'hide', {
					path: '/',
					expires: 10
				});
			}
		},
		show_toolbar: function(animate) {
			// Set up keybindings
			$(document).bind('keydown.djDebug', function(e) {
				if (e.keyCode == 27) {
					djdt.close();
				}
			});
			$('#djDebugToolbarHandle').hide();
			if (animate) {
				$('#djDebugToolbar').show('fast');
			} else {
				$('#djDebugToolbar').show();
			}
			$.cookie(COOKIE_NAME, null, {
				path: '/',
				expires: -1
			});
		},
		toggle_arrow: function(elem) {
			var uarr = String.fromCharCode(0x25b6);
			var darr = String.fromCharCode(0x25bc);
			elem.html(elem.html() == uarr ? darr : uarr);
		},
		ready: function(callback){
			if (djdt.isReady) {
				callback(djdt);
			} else {
				djdt.events.ready.push(callback);
			}
		}
	};
	$(document).ready(function() {
		djdt.init();
	});
	return djdt;
}(window, document, $djdtjq));


(function(window, document, $) {
	function _renderPerf() {
		// Browser timing remains hidden unless we can successfully access the performance object
		var perf = window.performance || window.msPerformance ||
					window.webkitPerformance || window.mozPerformance;
		if (perf) {
			var rowCount = 0,
				timingOffset = perf.timing.navigationStart,
				timingEnd = perf.timing.loadEventEnd;
			var totalTime = timingEnd - timingOffset;
			function getLeft(stat) {
				return ((perf.timing[stat] - timingOffset) / (totalTime)) * 100.0;
			}
			function getCSSWidth(stat, endStat) {
				var width = ((perf.timing[endStat] - perf.timing[stat]) / (totalTime)) * 100.0;
				// Calculate relative percent (same as sql panel logic)
				width = 100.0 * width / (100.0 - getLeft(stat));
				return (width < 1) ? "2px" : width + "%";
			}
			function addRow(stat, endStat) {
				rowCount++;
				var $row = $('<tr class="' + ((rowCount % 2) ? 'djDebugOdd' : 'djDebugEven') + '"></tr>');
				if (endStat) {
					// Render a start through end bar
					$row.html('<td>' + stat.replace('Start', '') + '</td>' +
					          '<td class="timeline"><div class="djDebugTimeline"><div class="djDebugLineChart" style="left:' + getLeft(stat) + '%;"><strong style="width:' + getCSSWidth(stat, endStat) + ';">&nbsp;</strong></div></div></td>' +
					          '<td>' + (perf.timing[stat] - timingOffset) + ' (+' + (perf.timing[endStat] - perf.timing[stat]) + ')</td>');
				} else {
					// Render a point in time
          $row.html('<td>' + stat + '</td>' +
                    '<td class="timeline"><div class="djDebugTimeline"><div class="djDebugLineChart" style="left:' + getLeft(stat) + '%;"><strong style="width:2px;">&nbsp;</strong></div></div></td>' +
                    '<td>' + (perf.timing[stat] - timingOffset) + '</td>');
				}
				$('#djDebugBrowserTimingTableBody').append($row);
			}

			// This is a reasonably complete and ordered set of timing periods (2 params) and events (1 param)
			addRow('domainLookupStart', 'domainLookupEnd');
			addRow('connectStart', 'connectEnd');
			addRow('requestStart', 'responseEnd') // There is no requestEnd
			addRow('responseStart', 'responseEnd');
			addRow('domLoading', 'domComplete'); // Spans the events below
			addRow('domInteractive');
			addRow('domContentLoadedEventStart', 'domContentLoadedEventEnd');
			addRow('loadEventStart', 'loadEventEnd');
			$('#djDebugBrowserTiming').css("display", "block");
		}
	}

	function renderPerf() {
		setTimeout(_renderPerf, 0);
	}

  $(window).bind('load', renderPerf);

}(window, document, $djdtjq));
