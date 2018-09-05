(function ($, publicAPI) {
    var $$ = {
        on: function(root, eventName, selector, fn) {
            root.addEventListener(eventName, function(event) {
                var target = event.target.closest(selector);
                if (root.contains(target)) {
                    fn.call(target, event);
                }
            });
        },
    };

    var onKeyDown = function(event) {
        if (event.keyCode == 27) {
            djdt.hide_one_level();
        }
    };

    var djdt = {
        handleDragged: false,
        events: {
            ready: []
        },
        isReady: false,
        init: function() {
            var djDebug = document.querySelector('#djDebug');
            djDebug.classList.remove('djdt-hidden');
            $$.on(djDebug.querySelector('#djDebugPanelList'), 'click', 'li a', function(event) {
                event.preventDefault();
                if (!this.className) {
                    return;
                }
                var current = $('#djDebug #' + this.className);
                if (current.is(':visible')) {
                    djdt.hide_panels();
                } else {
                    djdt.hide_panels();

                    current.show();
                    $(this).parent().addClass('djdt-active');

                    var inner = current.find('.djDebugPanelContent .djdt-scroll'),
                        store_id = $('#djDebug').data('store-id');
                    if (store_id && inner.children().length === 0) {
                        var ajax_data = {
                            data: {
                                store_id: store_id,
                                panel_id: this.className
                            },
                            type: 'GET',
                            url: $('#djDebug').data('render-panel-url')
                        };
                        $.ajax(ajax_data).done(function(data){
                            inner.prev().remove();  // Remove AJAX loader
                            inner.html(data);
                        }).fail(function(xhr){
                            var message = '<div class="djDebugPanelTitle"><a class="djDebugClose djDebugBack" href=""></a><h3>'+xhr.status+': '+xhr.statusText+'</h3></div>';
                            $('#djDebugWindow').html(message).show();
                        });
                    }
                }
            });
            $$.on(djDebug, 'click', 'a.djDebugClose', function(event) {
                event.preventDefault();
                djdt.hide_one_level();
            });
            $$.on(djDebug, 'click', '.djDebugPanelButton input[type=checkbox]', function() {
                djdt.cookie.set($(this).attr('data-cookie'), $(this).prop('checked') ? 'on' : 'off', {
                    path: '/',
                    expires: 10
                });
            });

            // Used by the SQL and template panels
            $$.on(djDebug, 'click', '.remoteCall', function(event) {
                event.preventDefault();

                var self = $(this);
                var name = self[0].tagName.toLowerCase();
                var ajax_data = {};

                if (name == 'button') {
                    var form = self.parents('form:eq(0)');
                    ajax_data.url = self.attr('formaction');

                    if (form.length) {
                        ajax_data.data = form.serialize();
                        ajax_data.type = form.attr('method') || 'POST';
                    }
                }

                if (name == 'a') {
                    ajax_data.url = self.attr('href');
                }

                $.ajax(ajax_data).done(function(data){
                    $('#djDebugWindow').html(data).show();
                }).fail(function(xhr){
                        var message = '<div class="djDebugPanelTitle"><a class="djDebugClose djDebugBack" href=""></a><h3>'+xhr.status+': '+xhr.statusText+'</h3></div>';
                        $('#djDebugWindow').html(message).show();
                });
            });

            // Used by the cache, profiling and SQL panels
            $$.on(djDebug, 'click', 'a.djToggleSwitch', function(event) {
                event.preventDefault();
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
            });

            djDebug.querySelector('#djHideToolBarButton').addEventListener('click', function(event) {
                event.preventDefault();
                djdt.hide_toolbar(true);
            });
            djDebug.querySelector('#djShowToolBarButton').addEventListener('click', function(event) {
                event.preventDefault();
                if (!djdt.handleDragged) {
                    djdt.show_toolbar();
                }
            });
            var startPageY, baseY;
            var handle = document.querySelector('#djDebugToolbarHandle');
            var onHandleMove = function(event) {
                // Chrome can send spurious mousemove events, so don't do anything unless the
                // cursor really moved.  Otherwise, it will be impossible to expand the toolbar
                // due to djdt.handleDragged being set to true.
                if (djdt.handleDragged || event.pageY != startPageY) {
                    var top = baseY + event.pageY;

                    if (top < 0) {
                        top = 0;
                    } else if (top + handle.offsetHeight > window.innerHeight) {
                        top = window.innerHeight - handle.offsetHeight;
                    }

                    handle.style.top = top + 'px';
                    djdt.handleDragged = true;
                }
            };
            djDebug.querySelector('#djShowToolBarButton').addEventListener('mousedown', function(event) {
                event.preventDefault();
                startPageY = event.pageY;
                baseY = handle.offsetTop - startPageY;
                document.addEventListener('mousemove', onHandleMove);
            });
            document.addEventListener('mouseup', function (event) {
                document.removeEventListener('mousemove', onHandleMove);
                if (djdt.handleDragged) {
                    event.preventDefault();
                    djdt.cookie.set('djdttop', handle.offsetTop, {
                        path: '/',
                        expires: 10
                    });
                    setTimeout(function () {
                        djdt.handleDragged = false;
                    }, 10);
                }
            });
            if (djdt.cookie.get('djdt') == 'hide') {
                djdt.hide_toolbar(false);
            } else {
                djdt.show_toolbar(false);
            }
            djdt.isReady = true;
            $.each(djdt.events.ready, function(_, callback){
                callback(djdt);
            });
        },
        hide_panels: function() {
            $('#djDebugWindow').hide();
            $('.djdt-panelContent').hide();
            $('#djDebugToolbar li').removeClass('djdt-active');
        },
        hide_toolbar: function(setCookie) {
            djdt.hide_panels();
            $('#djDebugToolbar').hide('fast');

            var handle = document.querySelector('#djDebugToolbarHandle');
            $(handle).show();
            // set handle position
            var handleTop = djdt.cookie.get('djdttop');
            if (handleTop) {
                handleTop = Math.min(handleTop, window.innerHeight - handle.offsetHeight);
                handle.style.top = handleTop + 'px';
            }

            // Unbind keydown
            document.removeEventListener('keydown', onKeyDown);

            if (setCookie) {
                djdt.cookie.set('djdt', 'hide', {
                    path: '/',
                    expires: 10
                });
            }
        },
        hide_one_level: function() {
            if ($('#djDebugWindow').is(':visible')) {
                $('#djDebugWindow').hide();
            } else if ($('.djdt-panelContent').is(':visible')) {
                djdt.hide_panels();
            } else {
                djdt.hide_toolbar(true);
            }
        },
        show_toolbar: function(animate) {
            // Set up keybindings
            document.addEventListener('keydown', onKeyDown);
            $('#djDebugToolbarHandle').hide();
            if (animate) {
                $('#djDebugToolbar').show('fast');
            } else {
                $('#djDebugToolbar').show();
            }
            djdt.cookie.set('djdt', 'show', {
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
        },
        cookie: {
            get: function(key){
                if (document.cookie.indexOf(key) === -1) return null;

                var cookieArray = document.cookie.split('; '),
                    cookies = {};

                cookieArray.forEach(function(e){
                    var parts = e.split('=');
                    cookies[ parts[0] ] = parts[1];
                });

                return cookies[ key ];
            },
            set: function(key, value, options){
                options = options || {};

                if (typeof options.expires === 'number') {
                    var days = options.expires, t = options.expires = new Date();
                    t.setDate(t.getDate() + days);
                }

                document.cookie = [
                    encodeURIComponent(key) + '=' + String(value),
                    options.expires ? '; expires=' + options.expires.toUTCString() : '',
                    options.path    ? '; path=' + options.path : '',
                    options.domain  ? '; domain=' + options.domain : '',
                    options.secure  ? '; secure' : ''
                ].join('');

                return value;
            }
        },
        applyStyle: function(name) {
            var selector = '#djDebug [data-' + name + ']';
            document.querySelectorAll(selector).forEach(function(element) {
                element.style[name] = element.getAttribute('data-' + name);
            });
        }
    };
    $.extend(publicAPI, {
        show_toolbar: djdt.show_toolbar,
        hide_toolbar: djdt.hide_toolbar,
        close: djdt.hide_one_level,
        cookie: djdt.cookie,
        applyStyle: djdt.applyStyle
    });
    $(document).ready(djdt.init);
})(djdt.jQuery, djdt);
