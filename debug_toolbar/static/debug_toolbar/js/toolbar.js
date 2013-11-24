(function (factory) {
    if (typeof define === 'function' && define.amd) {
        // AMD. Register as anonymous module.
        define(['jquery', 'jquery.cookie'], factory);
    } else {
        // Browser globals.
        window.djdt = factory(jQuery);
    }
}(function ($) {
    var djdt = {
        handleDragged: false,
        events: {
            ready: []
        },
        isReady: false,
        init: function() {
            $('#djDebug').show();
            var current = null;
            $(document).on('click', '#djDebugPanelList li a', function() {
                if (!this.className) {
                    return false;
                }
                current = $('#djDebug #' + this.className);
                if (current.is(':visible')) {
                    $(document).trigger('close.djDebug');
                    $(this).parent().removeClass('active');
                } else {
                    $('.panelContent').hide(); // Hide any that are already open
                    var inner = current.find('.djDebugPanelContent .scroll'),
                        store_id = $('#djDebug').data('store-id'),
                        render_panel_url = $('#djDebug').data('render-panel-url');
                    if (store_id !== '' && inner.children().length === 0) {
                        var ajax_data = {
                            data: {
                                store_id: store_id,
                                panel_id: this.className
                            },
                            type: 'GET',
                            url: render_panel_url
                        };
                        $.ajax(ajax_data).done(function(data){
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
            $(document).on('click', '#djDebug a.djDebugClose', function() {
                $(document).trigger('close.djDebug');
                $('#djDebugToolbar li').removeClass('active');
                return false;
            });
            $(document).on('click', '#djDebug .djDebugPanelButton input[type=checkbox]', function() {
                $.cookie($(this).attr('data-cookie'), $(this).prop('checked') ? 'on' : 'off', {
                    path: '/',
                    expires: 10,
                });
            });

            // Used by the SQL and template panels
            $(document).on('click', '#djDebug .remoteCall', function() {
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

                $(document).on('click', '#djDebugWindow a.djDebugBack', function() {
                    $(this).parent().parent().hide();
                    return false;
                });

                return false;
            });

            // Used by the cache, profiling and SQL panels
            $(document).on('click', '#djDebug a.djToggleSwitch', function(e) {
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
            if ($.cookie('djdt') == 'hide') {
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
            $.cookie('djdt', 'show', {
                path: '/',
                expires: 10
            });
        },
        ready: function(callback){
            if (djdt.isReady) {
                callback(djdt);
            } else {
                djdt.events.ready.push(callback);
            }
        }
    };
    $(document).ready(djdt.init);
    return djdt;
}));
