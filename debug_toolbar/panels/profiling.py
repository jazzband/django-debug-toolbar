from __future__ import division

from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
from debug_toolbar.panels import DebugPanel

try:
    from line_profiler import LineProfiler, show_func
    DJ_PROFILE_USE_LINE_PROFILER = True
except ImportError:
    DJ_PROFILE_USE_LINE_PROFILER = False


from cStringIO import StringIO
import cProfile
from pstats import Stats
from colorsys import hsv_to_rgb
import os


class DjangoDebugToolbarStats(Stats):
    __root = None

    def get_root_func(self):
        if self.__root is None:
            for func, (cc, nc, tt, ct, callers) in self.stats.iteritems():
                if len(callers) == 0:
                    self.__root = func
                    break
        return self.__root


class FunctionCall(object):
    def __init__(self, statobj, func, depth=0, stats=None,
                 id=0, parent_ids=[], hsv=(0,0.5,1)):
        self.statobj = statobj
        self.func = func
        if stats:
            self.stats = stats
        else:
            self.stats = statobj.stats[func][:4]
        self.depth = depth
        self.id = id
        self.parent_ids = parent_ids
        self.hsv = hsv
        self._line_stats_text = None

    def parent_classes(self):
        return self.parent_classes

    def background(self):
        r,g,b = hsv_to_rgb(*self.hsv)
        return 'rgb(%f%%,%f%%,%f%%)' %(r*100, g*100, b*100)

    def func_std_string(self): # match what old profile produced
        func_name = self.func
        if func_name[:2] == ('~', 0):
            # special case for built-in functions
            name = func_name[2]
            if name.startswith('<') and name.endswith('>'):
                return '{%s}' % name[1:-1]
            else:
                return name
        else:
            file_name, line_num, method = self.func
            idx = file_name.find('/site-packages/')
            if idx > -1:
                file_name = file_name[idx+14:]

            file_path, file_name = file_name.rsplit(os.sep, 1)

            return mark_safe('<span class="path">{0}/</span><span class="file">{1}</span> in <span class="func">{3}</span>(<span class="lineno">{2}</span>)'.format(
                file_path,
                file_name,
                line_num,
                method,
            ))

    def subfuncs(self):
        i=0
        h, s, v = self.hsv
        count = len(self.statobj.all_callees[self.func])
        for func, stats in self.statobj.all_callees[self.func].iteritems():
            i += 1
            h1 = h + (i/count)/(self.depth+1)
            if stats[3] == 0:
                s1 = 0
            else:
                s1 = s*(stats[3]/self.stats[3])
            yield FunctionCall(self.statobj,
                               func,
                               self.depth+1,
                               stats=stats,
                               id=str(self.id) + '_' + str(i),
                               parent_ids=self.parent_ids + [self.id],
                               hsv=(h1,s1,1))

    def count(self):
        return self.stats[1]

    def tottime(self):
        return self.stats[2]

    def cumtime(self):
        cc, nc, tt, ct = self.stats
        return self.stats[3]

    def tottime_per_call(self):
        cc, nc, tt, ct = self.stats

        if nc == 0:
            return 0

        return tt/nc

    def cumtime_per_call(self):
        cc, nc, tt, ct = self.stats

        if cc == 0:
            return 0

        return ct/cc

    def indent(self):
        return 16 * self.depth

    def line_stats_text(self):
        if self._line_stats_text is None and DJ_PROFILE_USE_LINE_PROFILER:
            lstats = self.statobj.line_stats
            if self.func in lstats.timings:
                out = StringIO()
                fn, lineno, name = self.func
                show_func(fn, lineno, name, lstats.timings[self.func], lstats.unit, stream=out)
                self._line_stats_text = out.getvalue()
            else:
                self._line_stats_text = False
        return self._line_stats_text

class ProfilingDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Profiling'
    template = 'debug_toolbar/panels/profiling.html'
    has_content = True

    def nav_title(self):
        return _('Profiling')

    def url(self):
        return ''

    def title(self):
        return _('Profiling')

    def _unwrap_closure_and_profile(self, func):
        if not hasattr(func, 'func_code'):
            return
        self.line_profiler.add_function(func)
        if func.func_closure:
            for cell in func.func_closure:
                if hasattr(cell.cell_contents, 'func_code'):
                    self._unwrap_closure_and_profile(cell.cell_contents)

    def process_view(self, request, view_func, view_args, view_kwargs):
        __traceback_hide__ = True
        self.profiler = cProfile.Profile()
        args = (request,) + view_args
        if DJ_PROFILE_USE_LINE_PROFILER:
            self.line_profiler = LineProfiler()
            self._unwrap_closure_and_profile(view_func)
            self.line_profiler.enable_by_count()
            out = self.profiler.runcall(view_func, *args, **view_kwargs)
            self.line_profiler.disable_by_count()
        else:
            self.line_profiler = None
            out = self.profiler.runcall(view_func, *args, **view_kwargs)
        return out

    def add_node(self, func_list, func, max_depth, cum_time=0.1):
        func_list.append(func)
        func.has_subfuncs = False
        if func.depth < max_depth:
            for subfunc in func.subfuncs():
                if (subfunc.stats[3] >= cum_time or
                   (hasattr(self.stats, 'line_stats') and
                   (subfunc.func in self.stats.line_stats.timings))):
                    func.has_subfuncs = True
                    self.add_node(func_list, subfunc, max_depth, cum_time=cum_time)

    def process_response(self, request, response):
        __traceback_hide__ = True
        if not hasattr(self, 'profiler'):
            return None
        self.profiler.create_stats()
        self.stats = DjangoDebugToolbarStats(self.profiler)
        if DJ_PROFILE_USE_LINE_PROFILER:
            self.stats.line_stats = self.line_profiler.get_stats()
        self.stats.calc_callees()

        root = FunctionCall(self.stats, self.stats.get_root_func(), depth=0)

        func_list = []
        self.add_node(func_list, root, 10, root.stats[3]/8)

        self.record_stats({'func_list': func_list})
