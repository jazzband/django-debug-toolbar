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

    def nav_subtitle(self):
        signals = self.get_stats()['signals']
        num_receivers = sum(len(s[2]) for s in signals)
        num_signals = len(signals)
        return '%d %s from %d %s' % (
            num_receivers,
            (num_receivers == 1) and 'receiver' or 'receivers',
            num_signals,
            (num_signals == 1) and 'signal' or 'signals',
        )

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
        for name, signal in sorted(self.signals.items(), key=lambda x: x[0]):
            if signal is None:
                continue
            receivers = []
            for (receiverkey, r_senderkey), receiver in signal.receivers:
                if isinstance(receiver, WEAKREF_TYPES):
                    receiver = receiver()
                if receiver is None:
                    continue

                receiver = getattr(receiver, '__wraps__', receiver)
                receiver_name = getattr(receiver, '__name__', str(receiver))
                if getattr(receiver, 'im_self', None) is not None:
                    text = "%s.%s" % (getattr(receiver.im_self, '__class__', type).__name__, receiver_name)
                elif getattr(receiver, 'im_class', None) is not None:
                    text = "%s.%s" % (receiver.im_class.__name__, receiver_name)
                else:
                    text = "%s" % receiver_name
                receivers.append(text)
            signals.append((name, signal, receivers))

        self.record_stats({'signals': signals})
