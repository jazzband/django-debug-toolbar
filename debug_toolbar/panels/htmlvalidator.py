import re

try:
    from tidylib import tidy_document
except ImportError:
    raise ImportError("""Please, make sure that PyTidyLib
        module installed - it's required for HTMLValidationDebugPanel""")

from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.safestring import mark_safe

from debug_toolbar.panels import DebugPanel


class HTMLValidationDebugPanel(DebugPanel):
    name = "HTMLValidator"
    has_content = True

    log_data = None
    errors_count = 0
    warns_count = 0
    src_content = ''

    def nav_title(self):
        return _("HTML Validator")

    def nav_subtitle(self):
        return mark_safe(_(u"Tidy Errors: %(errors_cnt)d "\
                            u"Warnings: %(warns_cnt)d") % {
            'errors_cnt': self.errors_count,
            'warns_cnt': self.warns_count,
            })

    def title(self):
        return _("HTML Validator")

    def url(self):
        return ''

    def process_response(self, request, response):
        document, errors = tidy_document(response.content,
                                         options={'numeric-entities': 1})
        self.log_data = (document, errors)
        self.src_content = response.content
        errors_list = errors.split('\n')
        self.errors_count = len([err for err in errors_list \
                                if 'error:' in err.lower()])
        self.warns_count = len([err for err in errors_list \
                                if 'warning:' in err.lower()])

        return response

    def appearance(self, errors):
        replacements = [
            (re.compile(r'\<([^\>]*)\>'), \
                '<strong class="code">&lt;\\1&gt;</strong>'),
            (re.compile(r'(line[^\-]*)(.*)'), \
                u'<td><pre class="handle-position">\\1</pre></td><td class="tidy-msg">\\2<td>'),
            (re.compile(r'\s*\-\s+(Error\:|Warning\:)', re.I), \
                        u'<i>\\1</i>'),
        ]

        for rx, rp in replacements:
            errors = re.sub(rx, rp, errors)

        errors_list = errors.split('\n')
        errors_rt = []
        # mark lines with error with validation-error class
        for err in errors_list:
            if 'error:' in err.lower():
                err = err.replace('<td>', '<td class="validation-error">')
                errors_rt.append(err)
                continue
            errors_rt.append(err)

        return errors_rt

    def content(self):
        context = self.context.copy()

        document, errors = self.log_data
        lines = self.src_content.split("\n")

        context.update({
        'document': document,
        'lines': zip(range(1, len(lines) + 1), lines),
        'errors': self.appearance(errors),
        })

        return render_to_string(\
                    'debug_toolbar/panels/htmlvalidator.html', context)
