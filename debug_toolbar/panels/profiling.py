import django
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe
import debug_toolbar
from debug_toolbar.panels import DebugPanel

import sys
import cProfile
from pstats import Stats, f8, func_std_string
from cStringIO import StringIO
from django.conf import settings
from colorsys import hsv_to_rgb

class DjangoDebugToolbarStats(Stats):
    __root = None
    
    def get_root_func(self):
        if self.__root is None:
            for func, (cc, nc, tt, ct, callers) in self.stats.iteritems():
                if len(callers) == 0:
                    self.__root = func
                    break
        return self.__root
    
    def print_call_tree_node(self, function, depth, max_depth, cum_filter=0.1):
        self.print_line(function, depth=depth)
        if depth < max_depth:
            for called in self.all_callees[function].keys():
                if self.stats[called][3] >= cum_filter:
                    self.print_call_tree_node(called, depth+1, max_depth, cum_filter=cum_filter)

class FunctionCall(object):
    def __init__(self, statobj, func, depth=0, stats=None,  css_id='djDebugProfileCall_0', hsv=(0,0.5,1)):
        self.statobj = statobj
        self.func = func
        if stats:
            self.stats = stats
        else:
            self.stats = statobj.stats[func][:4]
        self.depth = depth
        self.id = css_id
        self.hsv=hsv
    
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
            if file_name.startswith(settings.PROJECT_ROOT):
                file_name='PROJECT' + file_name[len(settings.PROJECT_ROOT):]
            idx = file_name.find('/site-packages/')
            if idx > -1:
                file_name=file_name[idx+14:]
            return "%s:%d(%s)" % (file_name, line_num, method)
    
    def subfuncs(self):
        i=0
        h,s,v = self.hsv
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
                               css_id=self.id + '_' + str(i),
                               hsv=(h1,s1,1))
    
    def as_row(self):
        cc, nc, tt, ct = self.stats
        if nc != cc:
            c = str(nc) + '/' + str(cc)
        else:
            c = str(nc)
            
        if nc != 0:
            ttdivnc = tt/nc
        else:
            ttdivnc = 0
        
        if cc == 0:
            ctdivcc = 0
        else:
            ctdivcc = ct/cc
        indent = 5*self.depth
        funcstr = self.func_std_string()
        out = """
                <td>%(c)s</td>
                <td>%(tt)8.3f<br/>(%(ttdivnc)8.3f)</td>
                <td>%(ct)8.3f<br/>(%(ctdivcc)8.3f)</td>
                <td style='padding-left:%(indent)ipx'>%(funcstr)s</td>
               """ % locals()
        return mark_safe(out)


class ProfilingDebugPanel(DebugPanel):
    """
    Panel that displays the Django version.
    """
    name = 'Profiling'
    has_content = True

    def nav_title(self):
        return _('Profiling')

    def url(self):
        return ''
    
    def title(self):
        return _('Profiling')

    def process_view(self, request, view_func, view_args, view_kwargs):
        self.profiler = cProfile.Profile()
        args = (request,) + view_args
        return self.profiler.runcall(view_func, *args, **view_kwargs)

    def process_response(self, request, response):
        self.profiler.create_stats()
        if 'djDebugProfileDump' in request.GET:
            self.profiler.dump_stats(settings.PROJECT_ROOT+'/'+request.GET.get('djDebugProfileDump', 'profile.out'))
        self.stats = DjangoDebugToolbarStats(self.profiler)
        return response

    def add_node(self, func_list, func, max_depth, cum_time=0.1):
        func_list.append(func)
        if func.depth < max_depth:
            for subfunc in func.subfuncs():
                if subfunc.stats[3] >= cum_time:
                    self.add_node(func_list, subfunc, max_depth, cum_time=cum_time)
    
    def content(self):
        
        self.stats.calc_callees()
        root = FunctionCall(self.stats, self.stats.get_root_func(), depth=0)
        
        func_list = []
        self.add_node(func_list, root, 10, root.stats[3]/16)
        context = self.context.copy()
        context.update({
            'func_list': func_list,
        })

        return render_to_string('debug_toolbar/panels/profiling.html', context)
