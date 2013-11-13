(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as anonymous module.
        define(['jquery', 'jquery.cookie'], factory);
    } else {
        // Browser globals.
        window.djdt = factory(jQuery);
    }
}(function (jQuery) {
    var $ = jQuery;
    var djdt = {
        handleDragged: false,
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
                    var inner = current.find('.djDebugPanelContent .scroll').first(),
                        storage_id = $('#djDebug').data('storage-id'),
                        render_panel_url = $('#djDebug').data('render-panel-url');
                    if (storage_id !== '' && inner.data('loaded') !== 'true') {
                        var ajax_data = {
                            data: {
                                storage_id: storage_id,
                                panel_id: this.className
                            },
                            type: 'GET',
                            url: render_panel_url
                        };
                        $.ajax(ajax_data).done(function(data){
                            inner.data('loaded', 'true');
                            inner.html(data);
                        }).fail(function(xhr){
                            var message = '<div class="djDebugPanelTitle"><a class="djDebugClose djDebugBack" href="">Back</a><h3>'+xhr.status+': '+xhr.statusText+'</h3></div>';
                            $('#djDebugWindow').html(message).show();
                        });
                    }
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
                if (!djdt.handleDragged) {
                    djdt.show_toolbar();
                }
                return false;
            });
            var handle = $('#djDebugToolbarHandle');
            $('#djShowToolBarButton').on('mousedown', function (event) {
                var baseY = handle.offset().top - event.pageY;
                $(document).on('mousemove', function (event) {
                    var offset = handle.offset();
                    offset.top = baseY + event.pageY;
                    handle.offset(offset);
                    djdt.handleDragged = true;
                });
                return false;
            });
            $(document).on('mouseup', function () {
                $(document).off('mousemove');
                if (djdt.handleDragged) {
                    var top = handle.offset().top;
                    $.cookie('djdttop', top, {
                        path: '/',
                        expires: 10
                    });
                    setTimeout(function () {
                        djdt.handleDragged = false;
                    }, 10);
                }
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
            if ($.cookie('djdt')) {
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
            // set handle position
            var handleTop = $.cookie('djdttop');
            if (handleTop) {
                $('#djDebugToolbarHandle').css({top: handleTop + 'px'});
            }
            // Unbind keydown
            $(document).unbind('keydown.djDebug');
            if (setCookie) {
                $.cookie('djdt', 'hide', {
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
            $.cookie('djdt', null, {
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

    function renderPerf() {
        // Browser timing remains hidden unless we can successfully access the performance object
        var perf = window.performance || window.msPerformance ||
                   window.webkitPerformance || window.mozPerformance;
        if (perf) {
            var rowCount = 0,
                timingOffset = perf.timing.navigationStart,
                timingEnd = perf.timing.loadEventEnd,
                totalTime = timingEnd - timingOffset;
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
            addRow('requestStart', 'responseEnd'); // There is no requestEnd
            addRow('responseStart', 'responseEnd');
            addRow('domLoading', 'domComplete'); // Spans the events below
            addRow('domInteractive');
            addRow('domContentLoadedEventStart', 'domContentLoadedEventEnd');
            addRow('loadEventStart', 'loadEventEnd');
            $('#djDebugBrowserTiming').css("display", "block");
        }
    }

    $(window).bind('load', function() {
        setTimeout(renderPerf, 0);
    });
    $(document).ready(function() {
        djdt.init();
    });

    return djdt;
}));
