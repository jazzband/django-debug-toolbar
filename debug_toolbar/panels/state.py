import re

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from debug_toolbar.panels import DebugPanel


class StateDebugPanel(DebugPanel):
    name = "State"
    has_content = True

    ADD = 1
    UPDATE = 2
    DELETE = 3

    objs_created = 0
    objs_deleted = 0
    objs_updated = 0

    objects_state = {}
    prev_objects_state = {}

    log_data = []

    keys = {ADD: 'created', UPDATE: 'updated', DELETE: 'deleted'}

    def nav_title(self):
        return _("State")

    def nav_subtitle(self):
        return mark_safe(_("%(created)d&nbsp;created, "\
                "%(updated)d&nbsp;changed, %(deleted)d&nbsp;deleted") % {
                'created': self.objs_created,
                'deleted': self.objs_deleted,
                'updated': self.objs_updated,
                })

    def title(self):
        return _("Objects State")

    def url(self):
        return ''

    def _track_save(cls, *args, **kwargs):
        """Method to track every post_save signal and increase amount of
        create/change action for corresponding object"""
        is_created = False
        action = cls.UPDATE
        if 'created' in kwargs and kwargs['created']:
            cls.objs_created += 1
            is_created = True
            action = cls.ADD
        else:
            cls.objs_updated += 1

        cls.log_data.append({
        'action': action,
        'sender': kwargs['sender'],
        'pk': kwargs['instance'].pk,
        'is_created': is_created,
        })
    track_save = classmethod(_track_save)

    def _track_delete(cls, *args, **kwargs):
        cls.objs_deleted += 1
        cls.log_data.append({
        'action': cls.DELETE,
        'pk': kwargs['instance'].pk,
        'sender': kwargs['sender'],
        })
    track_delete = classmethod(_track_delete)

    def _connect(cls):
        post_save.connect(cls.track_save)
        post_delete.connect(cls.track_delete)
        cls.update_objects_state()
    connect = classmethod(_connect)

    def _update_objects_state(cls):
        for md in models.get_models():
            model_name = cls.prepare_model_name(md)
            try:
                cls.objects_state[model_name] = md.objects.count()
            except Exception:
                pass
    update_objects_state = classmethod(_update_objects_state)

    def renew_state(self):
        cls = self.__class__

        cls.prev_objects_state = cls.objects_state.copy()
        self.update_objects_state()

        cls.objs_created = 0
        cls.objs_updated = 0
        cls.objs_deleted = 0
        cls.log_data = []

    def _prepare_model_name(cls, mdl):
        return re.sub(r'(\<class|[>\']*)', '', str(mdl)).strip()
    prepare_model_name = classmethod(_prepare_model_name)

    def _statistic(self):
        cls = self.__class__
        data = self.log_data
        stat = {}
        for item in data:
            sender = cls.prepare_model_name(item['sender'])
            action = item['action']
            if not sender in stat:
                stat[sender] = dict((key, 0) for key in self.keys.values())

            stat[sender][self.keys[action]] += 1

        return stat
    statistic = property(_statistic)

    def merge_states(self, stat, cur, prev):
        rv = []
        keys = self.keys.values()
        for md, cur in cur.iteritems():
            prev_amt = prev.get(md, -1)
            md_stat = stat.get(md, None)

            md_data = {
            'prev': prev_amt,
            'cur': cur,
            'model': md,
            }

            if md_stat:
                [md_data.update({
                'have_%s' % key: True,
                '%s_amount' % key: md_stat[key],
                }) for key in keys if md_stat[key] > 0]

            rv.append(md_data)

        # sort by C/U/D
        [rv.sort(reverse=True, key=lambda obj: obj.get(key, 0)) \
                    for key in ["%s_amount" % c_key for c_key in keys]]

        return rv

    def content(self):
        context = self.context.copy()
        statistic = self.statistic.copy()
        context.update({
        'objs_created': self.objs_created,
        'objs_updated': self.objs_updated,
        'objs_deleted': self.objs_deleted,
        'stat': statistic,
        'objects_state': self.merge_states(statistic, self.objects_state, \
                                            self.prev_objects_state),
        })

        # we should do it because we save state to
        # class, not to particular object instance
        self.renew_state()

        return render_to_string('debug_toolbar/panels/state.html', context)

# initialize tracking signals
StateDebugPanel.connect()
