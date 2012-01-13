import sys

from django.conf import settings
from django.core.signals import request_started, request_finished, \
    got_request_exception
from django.db.models.signals import class_prepared, pre_init, post_init, \
    pre_save, post_save, pre_delete, post_delete, post_syncdb
from django.dispatch.dispatcher import WEAKREF_TYPES
from django.utils.translation import ugettext_lazy as _

try:
    from django.db.backends.signals import connection_created
except ImportError:
    connection_created = None

from debug_toolbar.panels import DebugPanel

class SignalDebugPanel(DebugPanel):
    name = "Signals"
    template = 'debug_toolbar/panels/signals.html'
    has_content = True

    SIGNALS = {
        'request_started': request_started,
        'request_finished': request_finished,
        'got_request_exception': got_request_exception,
        'connection_created': connection_created,
        'class_prepared': class_prepared,
        'pre_init': pre_init,
        'post_init': post_init,
        'pre_save': pre_save,
        'post_save': post_save,
        'pre_delete': pre_delete,
        'post_delete': post_delete,
        'post_syncdb': post_syncdb,
    }

    def nav_title(self):
        return _("Signals")

    def title(self):
        return _("Signals")

    def url(self):
        return ''

    def signals(self):
        signals = self.SIGNALS.copy()
        if hasattr(settings, 'DEBUG_TOOLBAR_CONFIG'):
            extra_signals = settings.DEBUG_TOOLBAR_CONFIG.get('EXTRA_SIGNALS', [])
        else:
            extra_signals = []
        for signal in extra_signals:
            parts = signal.split('.')
            path = '.'.join(parts[:-1])
            __import__(path)
            signals[parts[-1]] = getattr(sys.modules[path], parts[-1])
        return signals
    signals = property(signals)

    def process_response(self, request, response):
        signals = []
        keys = self.signals.keys()
        keys.sort()
        for name in keys:
            signal = self.signals[name]
            if signal is None:
                continue
            receivers = []
            for (receiverkey, r_senderkey), receiver in signal.receivers:
                if isinstance(receiver, WEAKREF_TYPES):
                    receiver = receiver()
                if receiver is None:
                    continue
                if getattr(receiver, 'im_self', None) is not None:
                    text = "method %s on %s object" % (receiver.__name__, getattr(receiver.im_self, '__class__', type).__name__)
                elif getattr(receiver, 'im_class', None) is not None:
                    text = "method %s on %s" % (receiver.__name__, receiver.im_class.__name__)
                else:
                    text = "function %s" % getattr(receiver, '__name__', str(receiver))
                receivers.append(text)
            signals.append((name, signal, receivers))

        self.record_stats({'signals': signals})
